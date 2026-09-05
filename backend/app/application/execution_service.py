"""Execution service: turns a RoutingDecision into an actual (or simulated)
model call, with policy-safe automatic fallback.

Fallback rule: if the selected model fails, the NEXT candidate is taken from
the routing decision's already-ranked, already-eligible candidate list --
never from the excluded list. This guarantees fallback can never bypass a
hard policy violation (see app.domain.routing.engine for why exclusion is a
hard, separate stage).

Context-exhaustion rule: if a model fails specifically because the prompt
exceeded ITS context window (error_code == "CONTEXT_LENGTH_EXCEEDED"), it
would be pointless to fall back to another model with an equal or smaller
context window -- it would just fail the same way. So on that specific
failure, remaining candidates with context_window <= the failed model's are
dropped from the fallback queue before trying the next one. Any other
failure reason (timeout, rate limit, provider outage, ...) keeps the normal
ranked order, since context size wasn't the problem.
"""
from __future__ import annotations

from app.core.logging import log_event
from app.domain.execution.models import (
    ExecutionAttempt,
    ExecutionHistory,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from app.domain.routing.models import RankedCandidate, RoutingDecision
from app.infrastructure.providers.registry import build_adapter
from app.infrastructure.repositories.provider_repo import ProviderRepository
from app.infrastructure.repositories.routing_repo import RoutingRepository

DEFAULT_MAX_ATTEMPTS = 3
CONTEXT_LENGTH_EXCEEDED = "CONTEXT_LENGTH_EXCEEDED"


class ExecutionService:
    def __init__(
        self,
        provider_repo: ProviderRepository,
        routing_repo: RoutingRepository,
        provider_service_resolve_credentials=None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ):
        self.provider_repo = provider_repo
        self.routing_repo = routing_repo
        self._resolve_credentials = provider_service_resolve_credentials
        self.max_attempts = max_attempts

    async def execute_with_fallback(
        self, decision: RoutingDecision, prompt: str, max_tokens: int | None = None
    ) -> ExecutionHistory:
        history = ExecutionHistory(task_id=decision.task_id, routing_id=decision.routing_id)

        if not decision.is_successful():
            return history

        # Working queue of not-yet-tried candidates, in ranked (best-first)
        # order. This is mutated (filtered, not reordered) as we learn a
        # candidate failed due to context exhaustion.
        remaining: list[RankedCandidate] = list(decision.candidate_models)
        attempt_number = 0

        while remaining and attempt_number < self.max_attempts:
            candidate = remaining.pop(0)
            attempt_number += 1

            provider = await self.provider_repo.get(candidate.provider_id)
            if self._resolve_credentials:
                provider = self._resolve_credentials(provider)
            adapter = build_adapter(provider)

            request = ExecutionRequest(
                routing_id=decision.routing_id,
                task_id=decision.task_id,
                provider_id=candidate.provider_id,
                model_id=candidate.model_id,
                prompt=prompt,
                max_tokens=max_tokens,
                model_context_window=candidate.context_window,
            )

            log_event(
                "EXECUTION_STARTED",
                task_id=decision.task_id,
                routing_id=decision.routing_id,
                attempt=attempt_number,
                provider_id=candidate.provider_id,
                model_id=candidate.model_id,
                context_window=candidate.context_window,
            )

            result: ExecutionResult = await adapter.execute(request)

            attempt = ExecutionAttempt(
                routing_id=decision.routing_id,
                task_id=decision.task_id,
                attempt_number=attempt_number,
                provider_id=candidate.provider_id,
                model_id=candidate.model_id,
                result=result,
            )
            await self.routing_repo.save_attempt(attempt)
            history.attempts.append(attempt)

            if result.status == ExecutionStatus.SUCCEEDED:
                log_event(
                    "EXECUTION_SUCCEEDED",
                    task_id=decision.task_id,
                    routing_id=decision.routing_id,
                    attempt=attempt_number,
                    provider_id=candidate.provider_id,
                    model_id=candidate.model_id,
                )
                history.final_status = ExecutionStatus.SUCCEEDED
                history.final_provider_id = candidate.provider_id
                history.final_model_id = candidate.model_id
                return history

            log_event(
                "EXECUTION_FAILED",
                task_id=decision.task_id,
                routing_id=decision.routing_id,
                attempt=attempt_number,
                provider_id=candidate.provider_id,
                model_id=candidate.model_id,
                error_code=result.error_code,
            )

            if result.error_code == CONTEXT_LENGTH_EXCEEDED and remaining:
                before = len(remaining)
                remaining = [c for c in remaining if c.context_window > candidate.context_window]
                dropped = before - len(remaining)
                if dropped:
                    log_event(
                        "FALLBACK_CONTEXT_UPGRADE",
                        task_id=decision.task_id,
                        routing_id=decision.routing_id,
                        failed_context_window=candidate.context_window,
                        candidates_dropped=dropped,
                        candidates_remaining=len(remaining),
                    )

            if remaining:
                log_event("FALLBACK_STARTED", task_id=decision.task_id, routing_id=decision.routing_id)

        history.final_status = ExecutionStatus.FAILED
        return history
