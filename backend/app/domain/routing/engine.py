"""The routing engine: eligibility filtering (hard constraints) followed by
deterministic ranking (soft scoring).

This module deliberately does NOT know how any provider talks HTTP. It
operates purely against Provider / ModelSpec / Policy / ResourceSnapshot /
RoutingRequest and produces a RoutingDecision.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.models import Capability, ExecutionType, ModelSpec
from app.domain.policies.models import Policy
from app.domain.providers.models import Provider
from app.domain.resources.models import ResourceSnapshot
from app.domain.routing.models import (
    ExcludedCandidate,
    ExclusionReason,
    RankedCandidate,
    RoutingDecision,
    RoutingRequest,
    ScoreBreakdown,
)
from app.domain.tasks.models import PrivacyClassification


@dataclass
class Candidate:
    provider: Provider
    model: ModelSpec


class RoutingEngine:
    """Stage 1: eligibility filtering (hard constraints).
    Stage 2: ranking of only the eligible candidates (soft scoring).

    These stages are intentionally never merged into a single weighted
    score -- a high-capability model must never be able to outscore its
    way past a hard policy violation.
    """

    def route(
        self,
        request: RoutingRequest,
        policy: Policy,
        candidates: list[Candidate],
        resource_snapshot: ResourceSnapshot,
    ) -> RoutingDecision:
        eligible: list[Candidate] = []
        excluded: list[ExcludedCandidate] = []

        for candidate in candidates:
            reasons = self._eligibility_reasons(request, policy, candidate, resource_snapshot)
            if reasons:
                excluded.append(
                    ExcludedCandidate(
                        provider_id=candidate.provider.provider_id,
                        model_id=candidate.model.model_id,
                        reasons=reasons,
                    )
                )
            else:
                eligible.append(candidate)

        ranked = self._rank(eligible, request, policy)

        if not ranked:
            return RoutingDecision(
                task_id=request.task_id,
                selected_provider_id=None,
                selected_model_id=None,
                candidate_models=[],
                excluded_candidates=excluded,
                selection_score=None,
                decision_reasons=["No eligible candidates remained after hard-constraint filtering."],
                policy_applied=policy.policy_id,
            )

        best = ranked[0]
        return RoutingDecision(
            task_id=request.task_id,
            selected_provider_id=best.provider_id,
            selected_model_id=best.model_id,
            candidate_models=ranked,
            excluded_candidates=excluded,
            selection_score=best.score.total_score,
            decision_reasons=[f"Selected {best.model_id}: " + "; ".join(best.satisfied_reasons)],
            policy_applied=policy.policy_id,
        )

    # ---- Stage 1: eligibility -------------------------------------------------

    def _eligibility_reasons(
        self,
        request: RoutingRequest,
        policy: Policy,
        candidate: Candidate,
        resources: ResourceSnapshot,
    ) -> list[ExclusionReason]:
        provider, model = candidate.provider, candidate.model
        reasons: list[ExclusionReason] = []

        if not provider.enabled:
            reasons.append(ExclusionReason(code="PROVIDER_DISABLED", message="Provider is disabled."))
        if not provider.is_routable():
            reasons.append(
                ExclusionReason(code="PROVIDER_UNAVAILABLE", message="Provider is unhealthy or unavailable.")
            )
        if not model.enabled:
            reasons.append(ExclusionReason(code="MODEL_DISABLED", message="Model is disabled."))

        # Privacy / cloud-vs-local hard constraint
        privacy = PrivacyClassification(request.privacy_classification)
        if privacy not in policy.allowed_privacy_levels:
            reasons.append(
                ExclusionReason(
                    code="PRIVACY_LEVEL_NOT_ALLOWED",
                    message=f"Policy does not permit privacy level {privacy.value}.",
                )
            )
        if model.execution_type == ExecutionType.CLOUD and not policy.allow_cloud:
            reasons.append(
                ExclusionReason(code="CLOUD_PROHIBITED", message="Policy prohibits cloud execution.")
            )
        if model.execution_type == ExecutionType.LOCAL and not policy.allow_local:
            reasons.append(
                ExclusionReason(code="LOCAL_PROHIBITED", message="Policy prohibits local execution.")
            )

        # Provider allow/deny lists
        if policy.allowed_providers and provider.provider_id not in policy.allowed_providers:
            reasons.append(
                ExclusionReason(code="PROVIDER_NOT_ALLOWLISTED", message="Provider not in policy allowlist.")
            )
        if provider.provider_id in policy.denied_providers:
            reasons.append(
                ExclusionReason(code="PROVIDER_DENYLISTED", message="Provider is explicitly denied by policy.")
            )

        # Capability requirements (union of task + policy requirements)
        required_caps = {Capability(c) for c in request.required_capabilities} | policy.required_capabilities
        missing = {c for c in required_caps if not model.has_capability(c)}
        if missing:
            reasons.append(
                ExclusionReason(
                    code="MISSING_CAPABILITY",
                    message=f"Missing required capabilities: {', '.join(sorted(c.value for c in missing))}.",
                )
            )

        # Context window
        if request.min_context_window and model.context_window < request.min_context_window:
            reasons.append(
                ExclusionReason(
                    code="INSUFFICIENT_CONTEXT",
                    message=f"Context window {model.context_window} < required {request.min_context_window}.",
                )
            )

        # Cost ceiling (task-level then policy-level)
        cost_ceiling = request.max_estimated_cost_per_1k
        if policy.maximum_cost_per_1k is not None:
            cost_ceiling = (
                min(cost_ceiling, policy.maximum_cost_per_1k)
                if cost_ceiling is not None
                else policy.maximum_cost_per_1k
            )
        if cost_ceiling is not None:
            worst_cost = max(
                model.cost_metadata.estimated_input_cost_per_1k,
                model.cost_metadata.estimated_output_cost_per_1k,
            )
            if worst_cost > cost_ceiling:
                reasons.append(
                    ExclusionReason(
                        code="COST_EXCEEDS_BUDGET",
                        message=f"Estimated cost {worst_cost} exceeds budget {cost_ceiling}.",
                    )
                )

        # Latency ceiling
        latency_ceiling = request.max_estimated_latency_ms
        if policy.maximum_latency_ms is not None:
            latency_ceiling = (
                min(latency_ceiling, policy.maximum_latency_ms)
                if latency_ceiling is not None
                else policy.maximum_latency_ms
            )
        if (
            latency_ceiling is not None
            and model.latency_metadata.estimated_latency_ms > latency_ceiling
        ):
            reasons.append(
                ExclusionReason(
                    code="LATENCY_EXCEEDS_LIMIT",
                    message=(
                        f"Estimated latency {model.latency_metadata.estimated_latency_ms}ms "
                        f"exceeds limit {latency_ceiling}ms."
                    ),
                )
            )

        # Resource sufficiency (local models only)
        if model.execution_type == ExecutionType.LOCAL:
            req = model.resource_requirements
            if not resources.has_capacity_for(req.required_ram_gb, req.required_vram_gb):
                reasons.append(
                    ExclusionReason(
                        code="INSUFFICIENT_RESOURCES",
                        message=(
                            f"Requires {req.required_vram_gb}GB VRAM / {req.required_ram_gb}GB RAM; "
                            f"available {resources.vram_available_gb}GB VRAM / "
                            f"{resources.ram_available_gb}GB RAM."
                        ),
                    )
                )

        return reasons

    # ---- Stage 2: ranking -------------------------------------------------

    def _rank(
        self, eligible: list[Candidate], request: RoutingRequest, policy: Policy
    ) -> list[RankedCandidate]:
        if not eligible:
            return []

        max_cost = max(
            (max(c.model.cost_metadata.estimated_input_cost_per_1k,
                 c.model.cost_metadata.estimated_output_cost_per_1k) for c in eligible),
            default=0.0,
        ) or 1.0
        max_latency = max(
            (c.model.latency_metadata.estimated_latency_ms for c in eligible), default=0
        ) or 1
        max_caps = max((len(c.model.capabilities) for c in eligible), default=0) or 1

        ranked: list[RankedCandidate] = []
        for candidate in eligible:
            model = candidate.model
            satisfied = ["Provider permitted", "Privacy policy satisfied", "Hardware sufficient"]

            capability_score = len(model.capabilities) / max_caps
            worst_cost = max(
                model.cost_metadata.estimated_input_cost_per_1k,
                model.cost_metadata.estimated_output_cost_per_1k,
            )
            cost_score = 1.0 - (worst_cost / max_cost)
            latency_score = 1.0 - (model.latency_metadata.estimated_latency_ms / max_latency)
            reliability_score = model.reliability_metadata.configured_success_rate
            resource_score = 1.0 if model.execution_type == ExecutionType.LOCAL else 0.5
            preference_score = 1.0 if candidate.provider.provider_id in policy.allowed_providers else 0.5

            if request.required_capabilities:
                satisfied.insert(0, "Required capability match")
            if request.min_context_window:
                satisfied.append("Required context capacity")
            if policy.maximum_cost_per_1k is not None:
                satisfied.append("Within cost budget")
            if latency_score >= 0.5:
                satisfied.append("Lower estimated latency")

            total = (
                0.30 * capability_score
                + 0.20 * cost_score
                + 0.20 * latency_score
                + 0.20 * reliability_score
                + 0.05 * resource_score
                + 0.05 * preference_score
            )

            ranked.append(
                RankedCandidate(
                    provider_id=candidate.provider.provider_id,
                    model_id=model.model_id,
                    context_window=model.context_window,
                    score=ScoreBreakdown(
                        capability_score=round(capability_score, 4),
                        cost_score=round(cost_score, 4),
                        latency_score=round(latency_score, 4),
                        reliability_score=round(reliability_score, 4),
                        resource_score=round(resource_score, 4),
                        preference_score=round(preference_score, 4),
                        total_score=round(total, 4),
                    ),
                    satisfied_reasons=satisfied,
                )
            )

        ranked.sort(key=lambda r: r.score.total_score, reverse=True)
        return ranked
