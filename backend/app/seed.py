"""Seed data supporting the six demo scenarios from the Package 1 brief.

Run with: python -m app.seed  (against a fresh database)
"""
from __future__ import annotations

import asyncio

from app.domain.models.models import (
    Capability, CostMetadata, ExecutionType, LatencyMetadata,
    ModelCreate, ReliabilityMetadata, ResourceRequirements,
)
from app.domain.policies.models import PolicyCreate, PolicyPreset
from app.domain.providers.models import Provider, ProviderType
from app.domain.tasks.models import PrivacyClassification
from app.infrastructure.database.base import SessionLocal, init_models
from app.infrastructure.repositories.model_repo import ModelRepository
from app.infrastructure.repositories.policy_repo import PolicyRepository
from app.infrastructure.repositories.provider_repo import ProviderRepository


async def seed() -> None:
    await init_models()
    async with SessionLocal() as session:
        providers = ProviderRepository(session)
        models = ModelRepository(session)
        policies = PolicyRepository(session)

        # --- Providers -----------------------------------------------------
        # NOTE: ProviderRepository.add() takes a full `Provider` domain object
        # (it reads provider.health), not the `ProviderCreate` API DTO --
        # `ProviderCreate` has no `health` field, since health is
        # server-assigned, never client-supplied. The API layer goes through
        # ProviderService.create(), which does this same
        # Provider(**payload.model_dump()) construction; seed.py talks to the
        # repository directly, so it must build the domain object itself.
        await providers.add(Provider(
            provider_id="mock-cloud",
            name="Mock Cloud Provider",
            type=ProviderType.MOCK,
            metadata={"models": ["mock-cloud-large", "mock-cloud-vision"]},
        ))
        await providers.add(Provider(
            provider_id="mock-local",
            name="Mock Local Provider",
            type=ProviderType.MOCK,
            metadata={"models": ["mock-local-small", "mock-local-large"]},
        ))
        await providers.add(Provider(
            provider_id="mock-flaky",
            name="Mock Flaky Provider (Demo 5: fallback)",
            type=ProviderType.MOCK,
            metadata={"model_behaviors": {"mock-flaky-model": "model_failure"}, "models": ["mock-flaky-model"]},
        ))

        # --- Models ----------------------------------------------------------
        await models.add(ModelCreate(
            model_id="mock-cloud-large", provider_id="mock-cloud", display_name="Mock Cloud Large",
            capabilities={Capability.REASONING, Capability.CODING, Capability.LONG_CONTEXT, Capability.STRUCTURED_OUTPUT},
            context_window=128_000, execution_type=ExecutionType.CLOUD,
            cost_metadata=CostMetadata(estimated_input_cost_per_1k=1.0, estimated_output_cost_per_1k=3.0),
            latency_metadata=LatencyMetadata(estimated_latency_ms=1200),
            reliability_metadata=ReliabilityMetadata(configured_success_rate=0.98),
        ))
        await models.add(ModelCreate(
            model_id="mock-cloud-vision", provider_id="mock-cloud", display_name="Mock Cloud Vision",
            capabilities={Capability.VISION, Capability.REASONING}, context_window=64_000,
            supports_vision=True, execution_type=ExecutionType.CLOUD,
            cost_metadata=CostMetadata(estimated_input_cost_per_1k=1.5, estimated_output_cost_per_1k=4.0),
            latency_metadata=LatencyMetadata(estimated_latency_ms=1500),
        ))
        await models.add(ModelCreate(
            model_id="mock-local-small", provider_id="mock-local", display_name="Mock Local Small",
            capabilities={Capability.CODING, Capability.REASONING}, context_window=32_000,
            execution_type=ExecutionType.LOCAL,
            cost_metadata=CostMetadata(estimated_input_cost_per_1k=0.0, estimated_output_cost_per_1k=0.0),
            latency_metadata=LatencyMetadata(estimated_latency_ms=400),
            resource_requirements=ResourceRequirements(required_vram_gb=6, required_ram_gb=8),
        ))
        await models.add(ModelCreate(
            model_id="mock-local-large", provider_id="mock-local", display_name="Mock Local Large (Demo 4: needs 24GB VRAM)",
            capabilities={Capability.CODING, Capability.REASONING, Capability.LONG_CONTEXT}, context_window=100_000,
            execution_type=ExecutionType.LOCAL,
            cost_metadata=CostMetadata(estimated_input_cost_per_1k=0.0, estimated_output_cost_per_1k=0.0),
            latency_metadata=LatencyMetadata(estimated_latency_ms=900),
            resource_requirements=ResourceRequirements(required_vram_gb=24, required_ram_gb=32),
        ))
        await models.add(ModelCreate(
            model_id="mock-flaky-model", provider_id="mock-flaky", display_name="Mock Flaky Model",
            capabilities={Capability.CODING}, context_window=16_000, execution_type=ExecutionType.CLOUD,
            latency_metadata=LatencyMetadata(estimated_latency_ms=500),
        ))

        # --- Policies ----------------------------------------------------------
        await policies.add(PolicyCreate(
            policy_id="hybrid-default", name="Hybrid (default)", preset=PolicyPreset.HYBRID,
            allow_local=True, allow_cloud=True,
            allowed_privacy_levels={PrivacyClassification.PUBLIC, PrivacyClassification.INTERNAL},
        ))
        await policies.add(PolicyCreate(
            policy_id="sovereign-only", name="Sovereign (local-only)", preset=PolicyPreset.SOVEREIGN,
            allow_local=True, allow_cloud=False,
        ))
        await policies.add(PolicyCreate(
            policy_id="cloud-only", name="Cloud-preferred", preset=PolicyPreset.CLOUD,
            allow_local=False, allow_cloud=True,
        ))
        await policies.add(PolicyCreate(
            policy_id="economy", name="Economy (lowest cost)", preset=PolicyPreset.ECONOMY,
            allow_local=True, allow_cloud=True, maximum_cost_per_1k=0.5,
        ))

    print("Seed complete: 3 providers, 5 models, 4 policies.")


if __name__ == "__main__":
    asyncio.run(seed())
