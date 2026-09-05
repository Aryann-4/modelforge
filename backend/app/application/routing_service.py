from __future__ import annotations

from app.core.logging import log_event
from app.domain.routing.engine import Candidate, RoutingEngine
from app.domain.routing.models import RoutingDecision, RoutingRequest
from app.domain.tasks.models import Task
from app.infrastructure.repositories.model_repo import ModelRepository
from app.infrastructure.repositories.policy_repo import PolicyRepository
from app.infrastructure.repositories.provider_repo import ProviderRepository
from app.infrastructure.repositories.routing_repo import RoutingRepository
from app.infrastructure.resources.monitor import ResourceMonitor


class RoutingService:
    """Orchestrates: task -> policy -> candidate discovery -> RoutingEngine
    (eligibility filter + ranking) -> persisted RoutingDecision."""

    def __init__(
        self,
        provider_repo: ProviderRepository,
        model_repo: ModelRepository,
        policy_repo: PolicyRepository,
        routing_repo: RoutingRepository,
        resource_monitor: ResourceMonitor,
        engine: RoutingEngine | None = None,
    ):
        self.provider_repo = provider_repo
        self.model_repo = model_repo
        self.policy_repo = policy_repo
        self.routing_repo = routing_repo
        self.resource_monitor = resource_monitor
        self.engine = engine or RoutingEngine()

    async def route_task(self, task: Task, policy_id: str) -> RoutingDecision:
        log_event("ROUTING_STARTED", task_id=task.task_id, policy_id=policy_id)

        policy = await self.policy_repo.get(policy_id)
        providers = await self.provider_repo.list()
        candidates: list[Candidate] = []
        for provider in providers:
            models = await self.model_repo.list(provider_id=provider.provider_id)
            candidates.extend(Candidate(provider=provider, model=m) for m in models)

        log_event("CANDIDATES_FOUND", task_id=task.task_id, count=len(candidates))

        request = RoutingRequest(
            task_id=task.task_id,
            user_request=task.user_request,
            task_type=task.task_type.value,
            required_capabilities={c.value for c in task.requirements.required_capabilities},
            min_context_window=task.requirements.min_context_window,
            max_estimated_cost_per_1k=task.requirements.max_estimated_cost_per_1k,
            max_estimated_latency_ms=task.requirements.max_estimated_latency_ms,
            privacy_classification=task.privacy_classification.value,
            policy_id=policy_id,
        )

        snapshot = self.resource_monitor.snapshot()
        decision = self.engine.route(request, policy, candidates, snapshot)

        for excluded in decision.excluded_candidates:
            log_event(
                "CANDIDATE_REJECTED",
                task_id=task.task_id,
                model_id=excluded.model_id,
                reasons=[r.code for r in excluded.reasons],
            )

        if decision.is_successful():
            log_event(
                "MODEL_SELECTED",
                task_id=task.task_id,
                provider_id=decision.selected_provider_id,
                model_id=decision.selected_model_id,
                score=decision.selection_score,
            )
        else:
            log_event("ROUTING_FAILED", task_id=task.task_id, reason="no_eligible_candidates")

        await self.routing_repo.save_decision(decision)
        return decision
