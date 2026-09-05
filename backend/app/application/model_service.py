from __future__ import annotations

from app.core.logging import log_event
from app.domain.models.models import ModelCreate, ModelSpec, ModelUpdate
from app.infrastructure.repositories.model_repo import ModelRepository


class ModelService:
    def __init__(self, repo: ModelRepository):
        self.repo = repo

    async def create(self, payload: ModelCreate) -> ModelSpec:
        model = ModelSpec(**payload.model_dump())
        created = await self.repo.add(model)
        log_event("MODEL_REGISTERED", model_id=created.model_id, provider_id=created.provider_id)
        return created

    async def get(self, model_id: str) -> ModelSpec:
        return await self.repo.get(model_id)

    async def list(self, provider_id: str | None = None) -> list[ModelSpec]:
        return await self.repo.list(provider_id=provider_id)

    async def update(self, model_id: str, payload: ModelUpdate) -> ModelSpec:
        updated = await self.repo.update(model_id, **payload.model_dump(exclude_unset=True))
        log_event("MODEL_UPDATED", model_id=model_id)
        return updated

    async def delete(self, model_id: str) -> None:
        await self.repo.delete(model_id)
        log_event("MODEL_DELETED", model_id=model_id)
