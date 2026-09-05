from __future__ import annotations

from app.domain.policies.models import Policy, PolicyCreate
from app.infrastructure.repositories.policy_repo import PolicyRepository


class PolicyService:
    def __init__(self, repo: PolicyRepository):
        self.repo = repo

    async def create(self, payload: PolicyCreate) -> Policy:
        policy = Policy(**payload.model_dump())
        return await self.repo.add(policy)

    async def get(self, policy_id: str) -> Policy:
        return await self.repo.get(policy_id)

    async def list(self) -> list[Policy]:
        return await self.repo.list()
