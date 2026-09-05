from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.execution.models import ExecutionAttempt
from app.domain.routing.models import RoutingDecision
from app.infrastructure.database.orm import ExecutionAttemptORM, RoutingDecisionORM


class RoutingRepository:
    """Persists routing decisions and execution attempts (routing history)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_decision(self, decision: RoutingDecision) -> None:
        row = RoutingDecisionORM(
            routing_id=decision.routing_id,
            task_id=decision.task_id,
            selected_provider_id=decision.selected_provider_id,
            selected_model_id=decision.selected_model_id,
            candidate_models=[c.model_dump(mode="json") for c in decision.candidate_models],
            excluded_candidates=[c.model_dump(mode="json") for c in decision.excluded_candidates],
            selection_score=decision.selection_score,
            decision_reasons=decision.decision_reasons,
            policy_applied=decision.policy_applied,
        )
        self.session.add(row)
        await self.session.commit()

    async def save_attempt(self, attempt: ExecutionAttempt) -> None:
        row = ExecutionAttemptORM(
            attempt_id=attempt.attempt_id,
            routing_id=attempt.routing_id,
            task_id=attempt.task_id,
            attempt_number=attempt.attempt_number,
            provider_id=attempt.provider_id,
            model_id=attempt.model_id,
            result=attempt.result.model_dump(mode="json"),
        )
        self.session.add(row)
        await self.session.commit()

    async def get_attempts(self, routing_id: str) -> list[ExecutionAttempt]:
        result = await self.session.execute(
            select(ExecutionAttemptORM)
            .where(ExecutionAttemptORM.routing_id == routing_id)
            .order_by(ExecutionAttemptORM.attempt_number)
        )
        rows = result.scalars().all()
        return [
            ExecutionAttempt(
                attempt_id=r.attempt_id,
                routing_id=r.routing_id,
                task_id=r.task_id,
                attempt_number=r.attempt_number,
                provider_id=r.provider_id,
                model_id=r.model_id,
                result=r.result,
                timestamp=r.timestamp,
            )
            for r in rows
        ]
