"""Real HTTP adapter for OpenAI-compatible chat completion APIs.

Works against any endpoint implementing POST {base_url}/chat/completions,
which covers a large set of user-added providers without provider-specific
routing logic.
"""
from __future__ import annotations

import time

import httpx

from app.domain.execution.models import ExecutionRequest, ExecutionResult, ExecutionStatus
from app.domain.providers.models import ProviderHealth
from app.infrastructure.providers.base import ProviderAdapter

# Rough, provider-agnostic heuristic: ~4 characters per token for English
# text. This is intentionally conservative (it overestimates slightly) so we
# fail fast and re-route BEFORE spending a real API call on a prompt that's
# very likely too big, rather than after. It's a heuristic, not a real
# tokenizer -- documented as a prototype limitation.
_CHARS_PER_TOKEN_ESTIMATE = 4

# Substrings providers commonly use in their own "too many tokens" error
# messages, used to normalize a raw 400 response into CONTEXT_LENGTH_EXCEEDED.
_CONTEXT_ERROR_MARKERS = (
    "context_length_exceeded",
    "context length",
    "maximum context length",
    "too many tokens",
    "token limit",
    "exceeds the model's maximum",
)


def _looks_like_context_error(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _CONTEXT_ERROR_MARKERS)


class OpenAICompatibleAdapter(ProviderAdapter):
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = self.provider.metadata.get("_resolved_api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def health_check(self) -> ProviderHealth:
        if not self.provider.base_url:
            return ProviderHealth.UNHEALTHY
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.provider.base_url}/models", headers=self._headers())
                return ProviderHealth.HEALTHY if resp.status_code < 500 else ProviderHealth.UNHEALTHY
        except httpx.HTTPError:
            return ProviderHealth.UNHEALTHY

    async def list_models(self) -> list[str]:
        if not self.provider.base_url:
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.provider.base_url}/models", headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
                return [m.get("id") for m in data.get("data", []) if m.get("id")]
        except (httpx.HTTPError, ValueError, KeyError):
            return []

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.provider.base_url:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code="MISCONFIGURED_PROVIDER",
                error_message="Provider has no base_url configured.",
            )

        # Preemptive context-exhaustion check: estimate prompt tokens and
        # compare against the model's context window BEFORE calling the
        # provider. This lets the execution service re-route to a
        # larger-context model without wasting a real network round trip.
        if request.model_context_window:
            estimated_prompt_tokens = max(1, len(request.prompt) // _CHARS_PER_TOKEN_ESTIMATE)
            reserved_for_output = request.max_tokens or 512
            if estimated_prompt_tokens + reserved_for_output > request.model_context_window:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_code="CONTEXT_LENGTH_EXCEEDED",
                    error_message=(
                        f"Estimated prompt tokens (~{estimated_prompt_tokens}) plus reserved "
                        f"output ({reserved_for_output}) exceed this model's context window "
                        f"({request.model_context_window}). Estimate is heuristic (~"
                        f"{_CHARS_PER_TOKEN_ESTIMATE} chars/token), not an exact tokenizer count."
                    ),
                )

        payload = {
            "model": request.model_id,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        started = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=request.timeout_seconds) as client:
                resp = await client.post(
                    f"{self.provider.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
        except httpx.TimeoutException:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error_code="TIMEOUT",
                error_message="Request to provider timed out.",
                latency_ms=int((time.monotonic() - started) * 1000),
            )
        except httpx.ConnectError:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code="CONNECTION_ERROR",
                error_message="Could not connect to provider base_url.",
                latency_ms=int((time.monotonic() - started) * 1000),
            )
        except httpx.HTTPError as exc:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code="HTTP_ERROR",
                error_message=str(exc),
                latency_ms=int((time.monotonic() - started) * 1000),
            )

        latency_ms = int((time.monotonic() - started) * 1000)

        if resp.status_code == 401 or resp.status_code == 403:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, error_code="AUTHENTICATION_ERROR",
                error_message="Provider rejected credentials.", latency_ms=latency_ms,
            )
        if resp.status_code == 429:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, error_code="RATE_LIMITED",
                error_message="Provider rate-limited the request.", latency_ms=latency_ms,
            )
        if resp.status_code >= 500:
            return ExecutionResult(
                status=ExecutionStatus.FAILED, error_code="SERVER_ERROR",
                error_message=f"Provider returned {resp.status_code}.", latency_ms=latency_ms,
            )
        if resp.status_code >= 400:
            # Normalize the provider's own "too many tokens" phrasing into
            # our single CONTEXT_LENGTH_EXCEEDED code so the execution
            # service can make a routing decision on it, regardless of how
            # any individual provider words the error.
            if _looks_like_context_error(resp.text):
                return ExecutionResult(
                    status=ExecutionStatus.FAILED, error_code="CONTEXT_LENGTH_EXCEEDED",
                    error_message=f"Provider reported the context window was exceeded: {resp.text[:300]}",
                    latency_ms=latency_ms,
                )
            return ExecutionResult(
                status=ExecutionStatus.FAILED, error_code="BAD_REQUEST",
                error_message=f"Provider returned {resp.status_code}: {resp.text[:300]}",
                latency_ms=latency_ms,
            )

        try:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            return ExecutionResult(
                status=ExecutionStatus.FAILED, error_code="MALFORMED_RESPONSE",
                error_message="Provider response did not match the expected schema.",
                latency_ms=latency_ms,
            )

        return ExecutionResult(
            status=ExecutionStatus.SUCCEEDED, output_text=text, latency_ms=latency_ms,
        )
