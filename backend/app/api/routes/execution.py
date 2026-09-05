from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_execution_service
from app.application.execution_service import ExecutionService
from app.domain.routing.models import ExcludedCandidate, RankedCandidate, RoutingDecision
from app.infrastructure.database.orm import RoutingDecisionORM
from app.infrastructure.repositories.routing_repo import RoutingRepository

router = APIRouter(prefix="/api/v1/execution", tags=["execution"])


class ExecutePayload(BaseModel):
    routing_id: str
    prompt: str
    max_tokens: int | None = None


async def _load_decision(session: AsyncSession, routing_id: str) -> RoutingDecision:
    row = await session.get(RoutingDecisionORM, routing_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Routing decision '{routing_id}' not found.")
    return RoutingDecision(
        routing_id=row.routing_id,
        task_id=row.task_id,
        selected_provider_id=row.selected_provider_id,
        selected_model_id=row.selected_model_id,
        candidate_models=[RankedCandidate(**c) for c in row.candidate_models],
        excluded_candidates=[ExcludedCandidate(**c) for c in row.excluded_candidates],
        selection_score=row.selection_score,
        decision_reasons=row.decision_reasons,
        policy_applied=row.policy_applied,
        timestamp=row.timestamp,
    )


@router.post("/run")
async def run_execution(
    payload: ExecutePayload,
    session: AsyncSession = Depends(get_db),
    svc: ExecutionService = Depends(get_execution_service),
):
    decision = await _load_decision(session, payload.routing_id)
    history = await svc.execute_with_fallback(decision, payload.prompt, payload.max_tokens)
    return history.model_dump(mode="json")


@router.get("/history/{routing_id}")
async def get_history(routing_id: str, session: AsyncSession = Depends(get_db)):
    attempts = await RoutingRepository(session).get_attempts(routing_id)
    return [a.model_dump(mode="json") for a in attempts]
