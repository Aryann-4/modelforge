"""Deterministic mock provider adapter.

Lets the whole platform (routing, fallback, demos) be exercised without any
paid API. Behavior per model_id is configurable via provider.metadata so
tests/demos can deterministically request success, slow execution, or
failure. This is clearly a simulated adapter -- ExecutionResult.simulated
is always True.
"""
from __future__ import annotations

import asyncio

from app.domain.execution.models import ExecutionRequest, ExecutionResult, ExecutionStatus
from app.domain.providers.models import ProviderHealth
from app.infrastructure.providers.base import ProviderAdapter

# behavior can be: "success" | "slow" | "provider_failure" | "model_failure" | "context_exceeded"
_DEFAULT_BEHAVIOR = "success"


class MockProviderAdapter(ProviderAdapter):
    async def health_check(self) -> ProviderHealth:
        behavior = self.provider.metadata.get("behavior", _DEFAULT_BEHAVIOR)
        if behavior == "provider_failure":
            return ProviderHealth.UNHEALTHY
        return ProviderHealth.HEALTHY

    async def list_models(self) -> list[str]:
        return list(self.provider.metadata.get("models", []))

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        model_behaviors: dict[str, str] = self.provider.metadata.get("model_behaviors", {})
        behavior = model_behaviors.get(request.model_id, self.provider.metadata.get("behavior", _DEFAULT_BEHAVIOR))

        if behavior == "provider_failure":
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code="PROVIDER_UNAVAILABLE",
                error_message="Mock provider simulated a provider-level failure.",
                simulated=True,
            )
        if behavior == "model_failure":
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code="MODEL_ERROR",
                error_message=f"Mock model '{request.model_id}' simulated a failure.",
                simulated=True,
            )
        if behavior == "context_exceeded":
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error_code="CONTEXT_LENGTH_EXCEEDED",
                error_message=(
                    f"Mock model '{request.model_id}' simulated a context-window "
                    f"exhaustion (context_window={request.model_context_window})."
                ),
                simulated=True,
            )
        if behavior == "slow":
            await asyncio.sleep(min(request.timeout_seconds + 0.05, 0.2))
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error_code="TIMEOUT",
                error_message="Mock execution simulated a timeout.",
                latency_ms=int(request.timeout_seconds * 1000),
                simulated=True,
            )

        await asyncio.sleep(0.01)

        # Even in "success" mode, honor a genuinely oversized prompt against
        # this model's real context window, the same way the OpenAI-compatible
        # adapter does -- so a demo can send a very long prompt and see actual
        # context-exhaustion fallback, not just a scripted behavior flag.
        if request.model_context_window:
            estimated_prompt_tokens = max(1, len(request.prompt) // 4)
            reserved_for_output = request.max_tokens or 512
            if estimated_prompt_tokens + reserved_for_output > request.model_context_window:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    error_code="CONTEXT_LENGTH_EXCEEDED",
                    error_message=(
                        f"Mock model '{request.model_id}' context window "
                        f"({request.model_context_window}) exceeded by estimated prompt "
                        f"size (~{estimated_prompt_tokens} tokens)."
                    ),
                    simulated=True,
                )

        return ExecutionResult(
            status=ExecutionStatus.SUCCEEDED,
            output_text=f"[mock:{request.model_id}] simulated response to: {request.prompt[:120]!r}",
            latency_ms=10,
            simulated=True,
        )
