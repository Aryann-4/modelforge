"""Tests for context-window-exhaustion-aware fallback: on a
CONTEXT_LENGTH_EXCEEDED failure, remaining candidates with an equal-or-
smaller context window than the model that just failed must be skipped."""
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
        task_id="t1", user_request="a" * 400_000, task_type="GENERAL",
        privacy_classification=PrivacyClassification.INTERNAL.value, policy_id="pol1",
    )


@pytest.mark.asyncio
async def test_context_exceeded_skips_equal_or_smaller_models(db_session):
    """Small model is ranked first (cheap/fast/reliable), but its context
    window can't hold the prompt. A mid-size model ALSO can't hold it and
    must be skipped too -- fallback should land on the large-context model,
    not blindly try every ranked candidate in order."""
    provider = Provider(provider_id="p1", name="p1", type=ProviderType.MOCK, health=ProviderHealth.HEALTHY,
                         metadata={"behavior": "success"})
    await ProviderRepository(db_session).add(provider)

    small = ModelSpec(
        model_id="small", provider_id="p1", display_name="small", execution_type=ExecutionType.CLOUD,
        context_window=8_000,
        latency_metadata={"estimated_latency_ms": 100},
        reliability_metadata={"configured_success_rate": 0.99},
    )
    medium = ModelSpec(
        model_id="medium", provider_id="p1", display_name="medium", execution_type=ExecutionType.CLOUD,
        context_window=32_000,
        latency_metadata={"estimated_latency_ms": 200},
        reliability_metadata={"configured_success_rate": 0.95},
    )
    large = ModelSpec(
        model_id="large", provider_id="p1", display_name="large", execution_type=ExecutionType.CLOUD,
        context_window=200_000,
        latency_metadata={"estimated_latency_ms": 2000},
        reliability_metadata={"configured_success_rate": 0.80},
    )
    policy = Policy(policy_id="pol1", name="default")
    decision = RoutingEngine().route(
        _request(), policy,
        [Candidate(provider, small), Candidate(provider, medium), Candidate(provider, large)],
        _resources(),
    )
    # Small should rank first (fastest, most reliable, cheapest) despite
    # being unable to hold the (very long) prompt -- ranking has no idea
    # about THIS prompt's length, only the model's general profile.
    assert decision.selected_model_id == "small"

    svc = ExecutionService(
        ProviderRepository(db_session), RoutingRepository(db_session), max_attempts=5,
    )
    history = await svc.execute_with_fallback(decision, "a" * 400_000)

    assert history.final_status == ExecutionStatus.SUCCEEDED
    assert history.final_model_id == "large"
    # Exactly 2 attempts: small fails with CONTEXT_LENGTH_EXCEEDED, medium is
    # dropped from the queue (32k also < ~100k needed) without being tried,
    # large succeeds.
    assert len(history.attempts) == 2
    assert history.attempts[0].model_id == "small"
    assert history.attempts[0].result.error_code == "CONTEXT_LENGTH_EXCEEDED"
    assert history.attempts[1].model_id == "large"
    assert history.attempts[1].result.status == ExecutionStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_context_exceeded_with_no_larger_model_fails_cleanly(db_session):
    provider = Provider(provider_id="p1", name="p1", type=ProviderType.MOCK, health=ProviderHealth.HEALTHY,
                         metadata={"behavior": "success"})
    await ProviderRepository(db_session).add(provider)
    only_model = ModelSpec(
        model_id="only", provider_id="p1", display_name="only", execution_type=ExecutionType.CLOUD,
        context_window=4_000,
    )
    policy = Policy(policy_id="pol1", name="default")
    decision = RoutingEngine().route(
        _request(), policy, [Candidate(provider, only_model)], _resources(),
    )
    assert decision.selected_model_id == "only"

    svc = ExecutionService(ProviderRepository(db_session), RoutingRepository(db_session))
    history = await svc.execute_with_fallback(decision, "a" * 400_000)

    assert history.final_status == ExecutionStatus.FAILED
    assert len(history.attempts) == 1
    assert history.attempts[0].result.error_code == "CONTEXT_LENGTH_EXCEEDED"
