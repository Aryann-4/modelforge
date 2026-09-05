import pytest

from app.domain.models.models import Capability, ExecutionType, ModelSpec
from app.domain.policies.models import Policy, PolicyPreset
from app.domain.providers.models import Provider, ProviderHealth, ProviderType
from app.domain.resources.models import ResourceSnapshot
from app.domain.routing.engine import Candidate, RoutingEngine
from app.domain.routing.models import RoutingRequest
from app.domain.tasks.models import PrivacyClassification


def _provider(pid="p1", enabled=True) -> Provider:
    return Provider(provider_id=pid, name=pid, type=ProviderType.MOCK, enabled=enabled, health=ProviderHealth.HEALTHY)


def _model(mid="m1", pid="p1", execution_type=ExecutionType.CLOUD, **kw) -> ModelSpec:
    return ModelSpec(model_id=mid, provider_id=pid, display_name=mid, execution_type=execution_type, **kw)


def _resources() -> ResourceSnapshot:
    return ResourceSnapshot(
        cpu_count=8, cpu_utilization_pct=10, ram_total_gb=32, ram_available_gb=32,
        vram_total_gb=8, vram_available_gb=8, gpu_available=True, source="mock",
    )


def _request(**kw) -> RoutingRequest:
    base = dict(
        task_id="t1", user_request="hello", task_type="GENERAL",
        privacy_classification=PrivacyClassification.INTERNAL.value, policy_id="pol1",
    )
    base.update(kw)
    return RoutingRequest(**base)


def test_cloud_prohibited_excludes_cloud_models():
    policy = Policy(policy_id="pol1", name="sovereign", allow_local=True, allow_cloud=False)
    candidate = Candidate(provider=_provider(), model=_model(execution_type=ExecutionType.CLOUD))
    decision = RoutingEngine().route(_request(), policy, [candidate], _resources())
    assert decision.selected_model_id is None
    assert decision.excluded_candidates[0].reasons[0].code == "CLOUD_PROHIBITED"


def test_local_only_routing_selects_local_model():
    policy = Policy(policy_id="pol1", name="sovereign", allow_local=True, allow_cloud=False)
    candidates = [
        Candidate(provider=_provider(), model=_model("cloud-m", execution_type=ExecutionType.CLOUD)),
        Candidate(provider=_provider(), model=_model("local-m", execution_type=ExecutionType.LOCAL)),
    ]
    decision = RoutingEngine().route(_request(), policy, candidates, _resources())
    assert decision.selected_model_id == "local-m"


def test_provider_allowlist():
    policy = Policy(policy_id="pol1", name="allowlist", allowed_providers={"good-provider"})
    candidates = [
        Candidate(provider=_provider("good-provider"), model=_model("m1", "good-provider")),
        Candidate(provider=_provider("bad-provider"), model=_model("m2", "bad-provider")),
    ]
    decision = RoutingEngine().route(_request(), policy, candidates, _resources())
    assert decision.selected_provider_id == "good-provider"
    excluded_ids = {c.model_id for c in decision.excluded_candidates}
    assert "m2" in excluded_ids


def test_provider_denylist():
    policy = Policy(policy_id="pol1", name="denylist", denied_providers={"bad-provider"})
    candidates = [Candidate(provider=_provider("bad-provider"), model=_model("m1", "bad-provider"))]
    decision = RoutingEngine().route(_request(), policy, candidates, _resources())
    assert decision.selected_model_id is None
    assert decision.excluded_candidates[0].reasons[0].code == "PROVIDER_DENYLISTED"


def test_cost_limit_excludes_expensive_models():
    policy = Policy(policy_id="pol1", name="economy", maximum_cost_per_1k=0.1)
    from app.domain.models.models import CostMetadata
    expensive = _model("expensive", cost_metadata=CostMetadata(estimated_input_cost_per_1k=5.0))
    decision = RoutingEngine().route(_request(), policy, [Candidate(provider=_provider(), model=expensive)], _resources())
    assert decision.selected_model_id is None
    assert decision.excluded_candidates[0].reasons[0].code == "COST_EXCEEDS_BUDGET"


def test_latency_limit_excludes_slow_models():
    policy = Policy(policy_id="pol1", name="fast", maximum_latency_ms=100)
    from app.domain.models.models import LatencyMetadata
    slow = _model("slow", latency_metadata=LatencyMetadata(estimated_latency_ms=5000))
    decision = RoutingEngine().route(_request(), policy, [Candidate(provider=_provider(), model=slow)], _resources())
    assert decision.selected_model_id is None
    assert decision.excluded_candidates[0].reasons[0].code == "LATENCY_EXCEEDS_LIMIT"
