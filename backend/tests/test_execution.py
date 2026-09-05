import pytest

from app.application.execution_service import ExecutionService
from app.domain.execution.models import ExecutionStatus
from app.domain.models.models import ExecutionType, ModelSpec
from app.domain.policies.models import Policy
from app.domain.providers.models import Provider, ProviderHealth, ProviderType
from app.domain.resources.models import ResourceSnapshot
from app.domain.routing.engine import Candidate, RoutingEngine
from app.domain.routing.models import RoutingRequest
from app.domain.tasks.models import PrivacyClassification
from app.infrastructure.repositories.provider_repo import ProviderRepository
from app.infrastructure.repositories.routing_repo import RoutingRepository


def _resources() -> ResourceSnapshot:
    return ResourceSnapshot(
        cpu_count=8, cpu_utilization_pct=10, ram_total_gb=32, ram_available_gb=32,
        vram_total_gb=8, vram_available_gb=8, gpu_available=True, source="mock",
    )


def _request() -> RoutingRequest:
    return RoutingRequest(
        task_id="t1", user_request="hello", task_type="GENERAL",
        privacy_classification=PrivacyClassification.INTERNAL.value, policy_id="pol1",
    )


@pytest.mark.asyncio
async def test_mock_success(db_session):
    provider = Provider(provider_id="p1", name="p1", type=ProviderType.MOCK, health=ProviderHealth.HEALTHY,
                         metadata={"behavior": "success"})
    await ProviderRepository(db_session).add(provider)
    model = ModelSpec(model_id="m1", provider_id="p1", display_name="m1", execution_type=ExecutionType.CLOUD)
    policy = Policy(policy_id="pol1", name="default")
    decision = RoutingEngine().route(_request(), policy, [Candidate(provider, model)], _resources())

    svc = ExecutionService(ProviderRepository(db_session), RoutingRepository(db_session))
    history = await svc.execute_with_fallback(decision, "hi")
    assert history.final_status == ExecutionStatus.SUCCEEDED
    assert len(history.attempts) == 1


@pytest.mark.asyncio
async def test_mock_failure_and_fallback(db_session):
    failing = Provider(provider_id="failing", name="failing", type=ProviderType.MOCK, health=ProviderHealth.HEALTHY,
                        metadata={"behavior": "model_failure"})
    healthy = Provider(provider_id="healthy", name="healthy", type=ProviderType.MOCK, health=ProviderHealth.HEALTHY,
                        metadata={"behavior": "success"})
    repo = ProviderRepository(db_session)
    await repo.add(failing)
    await repo.add(healthy)

    model_a = ModelSpec(model_id="model-a", provider_id="failing", display_name="A",
                         execution_type=ExecutionType.CLOUD,
                         reliability_metadata={"configured_success_rate": 0.99})
    model_b = ModelSpec(model_id="model-b", provider_id="healthy", display_name="B",
                         execution_type=ExecutionType.CLOUD,
                         reliability_metadata={"configured_success_rate": 0.5})
    policy = Policy(policy_id="pol1", name="default")
    decision = RoutingEngine().route(
        _request(), policy, [Candidate(failing, model_a), Candidate(healthy, model_b)], _resources()
    )
    # model-a should rank first (higher configured reliability) -- fallback should reach model-b.
    assert decision.selected_model_id == "model-a"

    svc = ExecutionService(ProviderRepository(db_session), RoutingRepository(db_session))
    history = await svc.execute_with_fallback(decision, "hi")
    assert history.final_status == ExecutionStatus.SUCCEEDED
    assert history.final_model_id == "model-b"
    assert len(history.attempts) == 2
    assert history.attempts[0].result.status == ExecutionStatus.FAILED
    assert history.attempts[1].result.status == ExecutionStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_provider_timeout(db_session):
    provider = Provider(provider_id="p1", name="p1", type=ProviderType.MOCK, health=ProviderHealth.HEALTHY,
                         metadata={"behavior": "slow"})
    await ProviderRepository(db_session).add(provider)
    model = ModelSpec(model_id="m1", provider_id="p1", display_name="m1", execution_type=ExecutionType.CLOUD)
    policy = Policy(policy_id="pol1", name="default")
    decision = RoutingEngine().route(_request(), policy, [Candidate(provider, model)], _resources())

    svc = ExecutionService(ProviderRepository(db_session), RoutingRepository(db_session))
    history = await svc.execute_with_fallback(decision, "hi")
    assert history.attempts[0].result.status == ExecutionStatus.TIMEOUT
    assert history.final_status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_policy_safe_fallback_never_uses_excluded_candidate(db_session):
    """If cloud is prohibited, a failing local model must NOT fall back to a
    cloud model even though the cloud model was never even considered."""
    local_failing = Provider(provider_id="local-p", name="local", type=ProviderType.MOCK,
                              health=ProviderHealth.HEALTHY, metadata={"behavior": "model_failure"})
    cloud_provider = Provider(provider_id="cloud-p", name="cloud", type=ProviderType.MOCK,
                               health=ProviderHealth.HEALTHY, metadata={"behavior": "success"})
    repo = ProviderRepository(db_session)
    await repo.add(local_failing)
    await repo.add(cloud_provider)

    local_model = ModelSpec(model_id="local-m", provider_id="local-p", display_name="L",
                             execution_type=ExecutionType.LOCAL)
    cloud_model = ModelSpec(model_id="cloud-m", provider_id="cloud-p", display_name="C",
                             execution_type=ExecutionType.CLOUD)
    policy = Policy(policy_id="pol1", name="sovereign", allow_local=True, allow_cloud=False)
    decision = RoutingEngine().route(
        _request(), policy, [Candidate(local_failing, local_model), Candidate(cloud_provider, cloud_model)], _resources()
    )
    # cloud-m must have been excluded at routing time already.
    assert decision.selected_model_id == "local-m"
    assert any(c.model_id == "cloud-m" for c in decision.excluded_candidates)

    svc = ExecutionService(ProviderRepository(db_session), RoutingRepository(db_session))
    history = await svc.execute_with_fallback(decision, "hi")
    # Only the eligible candidate list (just local-m) was available to fall back through.
    assert history.final_status == ExecutionStatus.FAILED
    assert all(a.provider_id != "cloud-p" for a in history.attempts)
