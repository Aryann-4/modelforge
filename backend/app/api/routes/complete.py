"""The "just answer this" endpoint: the single call a caller makes when they
don't want to think about task classification, model selection, policies, or
fallback at all. Wraps task creation -> routing -> execution-with-fallback
(including context-exhaustion-aware re-routing) into one request/response.

This is the "brain" surface of ModelForge: give it a prompt, get an answer,
and the actual model/provider that produced it is reported back for
transparency -- but never something the caller has to pick themselves.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_execution_service, get_routing_service, get_task_service
from app.application.execution_service import ExecutionService
from app.application.routing_service import RoutingService
from app.application.task_service import TaskService
from app.core.config import settings
from app.core.errors import NotFoundError
from app.domain.execution.models import ExecutionStatus
from app.domain.tasks.models import PrivacyClassification, TaskCreate

router = APIRouter(prefix="/api/v1", tags=["complete"])


class CompleteRequest(BaseModel):
    prompt: str = Field(..., description="The task/prompt to run. Model selection is fully automatic.")
    privacy_classification: PrivacyClassification = PrivacyClassification.INTERNAL
    policy_id: str | None = Field(
        default=None,
        description="Optional. Defaults to MODELFORGE_DEFAULT_POLICY_ID (hybrid-default) if omitted.",
    )
    max_tokens: int | None = None


class AttemptSummary(BaseModel):
    attempt_number: int
    provider_id: str
    model_id: str
    status: str
    error_code: str | None = None


class CompleteResponse(BaseModel):
    succeeded: bool
    answer: str | None
    provider_id: str | None
    model_id: str | None
    task_type: str
    routing_id: str | None
    attempts: list[AttemptSummary]
    decision_reasons: list[str]


@router.post("/complete", response_model=CompleteResponse)
async def complete(
    payload: CompleteRequest,
    task_svc: TaskService = Depends(get_task_service),
    routing_svc: RoutingService = Depends(get_routing_service),
    execution_svc: ExecutionService = Depends(get_execution_service),
) -> CompleteResponse:
    policy_id = payload.policy_id or settings.default_policy_id

    # 1. Task type/requirements are auto-classified -- the caller never
    #    specifies a model or even a task type.
    task = await task_svc.create(TaskCreate(
        user_request=payload.prompt,
        privacy_classification=payload.privacy_classification,
        policy_id=policy_id,
    ))

    # 2. Route: hard-constraint eligibility filter, then ranking. Raises
    #    NotFoundError (-> 404) only if policy_id itself doesn't exist; an
    #    empty eligible set is NOT an error, it's a normal "no capable/
    #    allowed model" result.
    try:
        decision = await routing_svc.route_task(task, policy_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    if not decision.is_successful():
        return CompleteResponse(
            succeeded=False,
            answer=None,
            provider_id=None,
            model_id=None,
            task_type=task.task_type.value,
            routing_id=decision.routing_id,
            attempts=[],
            decision_reasons=decision.decision_reasons,
        )

    # 3. Execute with automatic fallback. Context-window exhaustion is
    #    detected per-attempt (either preemptively or from the provider's own
    #    error) and, on that specific failure, remaining candidates with an
    #    equal-or-smaller context window are skipped -- so fallback actually
    #    reaches a model that can fit the prompt, instead of retrying models
    #    that would fail the same way.
    history = await execution_svc.execute_with_fallback(decision, payload.prompt, payload.max_tokens)

    final_attempt = history.attempts[-1] if history.attempts else None
    succeeded = history.final_status == ExecutionStatus.SUCCEEDED

    return CompleteResponse(
        succeeded=succeeded,
        answer=final_attempt.result.output_text if succeeded and final_attempt else None,
        provider_id=history.final_provider_id,
        model_id=history.final_model_id,
        task_type=task.task_type.value,
        routing_id=decision.routing_id,
        attempts=[
            AttemptSummary(
                attempt_number=a.attempt_number,
                provider_id=a.provider_id,
                model_id=a.model_id,
                status=a.result.status.value,
                error_code=a.result.error_code,
            )
            for a in history.attempts
        ],
        decision_reasons=decision.decision_reasons,
    )
