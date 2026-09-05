from app.domain.models.models import (
    Capability, ExecutionType, ModelSpec, ResourceRequirements,
)
from app.domain.policies.models import Policy
from app.domain.providers.models import Provider, ProviderHealth, ProviderType
from app.domain.resources.models import ResourceSnapshot
from app.domain.routing.engine import Candidate, RoutingEngine
from app.domain.routing.models import RoutingRequest
from app.domain.tasks.models import PrivacyClassification


def _provider(pid="p1") -> Provider:
    return Provider(provider_id=pid, name=pid, type=ProviderType.MOCK, health=ProviderHealth.HEALTHY)


def _resources(vram=8.0) -> ResourceSnapshot:
    return ResourceSnapshot(
        cpu_count=8, cpu_utilization_pct=10, ram_total_gb=32, ram_available_gb=32,
        vram_total_gb=vram, vram_available_gb=vram, gpu_available=True, source="mock",
    )


def _request(**kw) -> RoutingRequest:
    base = dict(
        task_id="t1", user_request="hello", task_type="GENERAL",
        privacy_classification=PrivacyClassification.INTERNAL.value, policy_id="pol1",
    )
    base.update(kw)
    return RoutingRequest(**base)


def test_coding_task_selects_coding_model():
    policy = Policy(policy_id="pol1", name="default")
    candidates = [
        Candidate(_provider(), ModelSpec(model_id="general", provider_id="p1", display_name="g")),
        Candidate(_provider(), ModelSpec(
            model_id="coder", provider_id="p1", display_name="c", capabilities={Capability.CODING}
        )),
    ]
    decision = RoutingEngine().route(
        _request(required_capabilities={"coding"}), policy, candidates, _resources()
    )
    assert decision.selected_model_id == "coder"


def test_vision_task_rejects_non_vision_models():
    policy = Policy(policy_id="pol1", name="default")
    candidates = [
        Candidate(_provider(), ModelSpec(model_id="text-only", provider_id="p1", display_name="t")),
        Candidate(_provider(), ModelSpec(
            model_id="vision-model", provider_id="p1", display_name="v", capabilities={Capability.VISION}
        )),
    ]
    decision = RoutingEngine().route(
        _request(required_capabilities={"vision"}), policy, candidates, _resources()
    )
    assert decision.selected_model_id == "vision-model"
    rejected_ids = {c.model_id for c in decision.excluded_candidates}
    assert "text-only" in rejected_ids


def test_context_requirements_reject_insufficient_models():
    policy = Policy(policy_id="pol1", name="default")
    candidates = [
        Candidate(_provider(), ModelSpec(model_id="small-ctx", provider_id="p1", display_name="s", context_window=4000)),
        Candidate(_provider(), ModelSpec(model_id="big-ctx", provider_id="p1", display_name="b", context_window=200_000)),
    ]
    decision = RoutingEngine().route(
        _request(min_context_window=100_000), policy, candidates, _resources()
    )
    assert decision.selected_model_id == "big-ctx"


def test_privacy_rules_exclude_cloud_models():
    from app.domain.tasks.models import PrivacyClassification as PC
    policy = Policy(policy_id="pol1", name="restricted", allowed_privacy_levels={PC.PUBLIC})
    candidates = [Candidate(_provider(), ModelSpec(model_id="m", provider_id="p1", display_name="m"))]
    decision = RoutingEngine().route(
        _request(privacy_classification=PC.CONFIDENTIAL.value), policy, candidates, _resources()
    )
    assert decision.selected_model_id is None
    assert decision.excluded_candidates[0].reasons[0].code == "PRIVACY_LEVEL_NOT_ALLOWED"


def test_disabled_providers_are_excluded():
    policy = Policy(policy_id="pol1", name="default")
    disabled_provider = Provider(provider_id="p1", name="p1", type=ProviderType.MOCK, enabled=False)
    candidates = [Candidate(disabled_provider, ModelSpec(model_id="m", provider_id="p1", display_name="m"))]
    decision = RoutingEngine().route(_request(), policy, candidates, _resources())
    assert decision.selected_model_id is None
    codes = {r.code for r in decision.excluded_candidates[0].reasons}
    assert "PROVIDER_DISABLED" in codes


def test_insufficient_vram_excludes_local_models():
    policy = Policy(policy_id="pol1", name="default")
    big_local = ModelSpec(
        model_id="big-local", provider_id="p1", display_name="big", execution_type=ExecutionType.LOCAL,
        resource_requirements=ResourceRequirements(required_vram_gb=24, required_ram_gb=32),
    )
    decision = RoutingEngine().route(
        _request(), policy, [Candidate(_provider(), big_local)], _resources(vram=8.0)
    )
    assert decision.selected_model_id is None
    assert decision.excluded_candidates[0].reasons[0].code == "INSUFFICIENT_RESOURCES"


def test_ranking_chooses_best_eligible_model():
    from app.domain.models.models import CostMetadata, LatencyMetadata, ReliabilityMetadata
    policy = Policy(policy_id="pol1", name="default")
    cheap_fast = ModelSpec(
        model_id="cheap-fast", provider_id="p1", display_name="cf",
        capabilities={Capability.CODING},
        cost_metadata=CostMetadata(estimated_input_cost_per_1k=0.1),
        latency_metadata=LatencyMetadata(estimated_latency_ms=100),
        reliability_metadata=ReliabilityMetadata(configured_success_rate=0.99),
    )
    expensive_slow = ModelSpec(
        model_id="expensive-slow", provider_id="p1", display_name="es",
        capabilities={Capability.CODING},
        cost_metadata=CostMetadata(estimated_input_cost_per_1k=10.0),
        latency_metadata=LatencyMetadata(estimated_latency_ms=5000),
        reliability_metadata=ReliabilityMetadata(configured_success_rate=0.80),
    )
    decision = RoutingEngine().route(
        _request(), policy, [Candidate(_provider(), cheap_fast), Candidate(_provider(), expensive_slow)], _resources()
    )
    assert decision.selected_model_id == "cheap-fast"
