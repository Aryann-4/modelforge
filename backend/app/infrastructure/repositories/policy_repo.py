from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domain.models.models import Capability
from app.domain.policies.models import Policy, PolicyPreset
from app.domain.tasks.models import PrivacyClassification
from app.infrastructure.database.orm import PolicyORM


def _to_domain(row: PolicyORM) -> Policy:
    return Policy(
        policy_id=row.policy_id,
        name=row.name,
        preset=PolicyPreset(row.preset),
        allow_local=row.allow_local,
        allow_cloud=row.allow_cloud,
        allowed_providers=set(row.allowed_providers or []),
        denied_providers=set(row.denied_providers or []),
        maximum_cost_per_1k=row.maximum_cost_per_1k,
        maximum_latency_ms=row.maximum_latency_ms,
        required_capabilities={Capability(c) for c in (row.required_capabilities or [])},
        allowed_privacy_levels={PrivacyClassification(c) for c in (row.allowed_privacy_levels or [])},
        metadata=row.policy_metadata or {},
    )


class PolicyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, policy: Policy) -> Policy:
        row = PolicyORM(
            policy_id=policy.policy_id,
            name=policy.name,
            preset=policy.preset.value,
            allow_local=policy.allow_local,
            allow_cloud=policy.allow_cloud,
            allowed_providers=list(policy.allowed_providers),
            denied_providers=list(policy.denied_providers),
            maximum_cost_per_1k=policy.maximum_cost_per_1k,
            maximum_latency_ms=policy.maximum_latency_ms,
            required_capabilities=[c.value for c in policy.required_capabilities],
            allowed_privacy_levels=[p.value for p in policy.allowed_privacy_levels],
            policy_metadata=policy.metadata,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def get(self, policy_id: str) -> Policy:
        row = await self.session.get(PolicyORM, policy_id)
        if row is None:
            raise NotFoundError(f"Policy '{policy_id}' not found.")
        return _to_domain(row)

    async def list(self) -> list[Policy]:
        result = await self.session.execute(select(PolicyORM))
        return [_to_domain(r) for r in result.scalars().all()]

    async def exists(self, policy_id: str) -> bool:
        row = await self.session.get(PolicyORM, policy_id)
        return row is not None
