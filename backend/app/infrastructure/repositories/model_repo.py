from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domain.models.models import (
    Capability,
    CostMetadata,
    ExecutionType,
    LatencyMetadata,
    ModelSpec,
    ReliabilityMetadata,
    ResourceRequirements,
)
from app.infrastructure.database.orm import ModelORM


def _to_domain(row: ModelORM) -> ModelSpec:
    return ModelSpec(
        model_id=row.model_id,
        provider_id=row.provider_id,
        display_name=row.display_name,
        capabilities={Capability(c) for c in (row.capabilities or [])},
        context_window=row.context_window,
        max_output_tokens=row.max_output_tokens,
        supports_streaming=row.supports_streaming,
        supports_tools=row.supports_tools,
        supports_vision=row.supports_vision,
        execution_type=ExecutionType(row.execution_type),
        cost_metadata=CostMetadata(**(row.cost_metadata or {})),
        latency_metadata=LatencyMetadata(**(row.latency_metadata or {})),
        resource_requirements=ResourceRequirements(**(row.resource_requirements or {})),
        reliability_metadata=ReliabilityMetadata(**(row.reliability_metadata or {})),
        enabled=row.enabled,
        metadata=row.model_metadata or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class ModelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, model: ModelSpec) -> ModelSpec:
        row = ModelORM(
            model_id=model.model_id,
            provider_id=model.provider_id,
            display_name=model.display_name,
            capabilities=[c.value for c in model.capabilities],
            context_window=model.context_window,
            max_output_tokens=model.max_output_tokens,
            supports_streaming=model.supports_streaming,
            supports_tools=model.supports_tools,
            supports_vision=model.supports_vision,
            execution_type=model.execution_type.value,
            cost_metadata=model.cost_metadata.model_dump(),
            latency_metadata=model.latency_metadata.model_dump(),
            resource_requirements=model.resource_requirements.model_dump(),
            reliability_metadata=model.reliability_metadata.model_dump(),
            enabled=model.enabled,
            model_metadata=model.metadata,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def get(self, model_id: str) -> ModelSpec:
        result = await self.session.execute(select(ModelORM).where(ModelORM.model_id == model_id))
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError(f"Model '{model_id}' not found.")
        return _to_domain(row)

    async def list(self, provider_id: str | None = None) -> list[ModelSpec]:
        query = select(ModelORM)
        if provider_id:
            query = query.where(ModelORM.provider_id == provider_id)
        result = await self.session.execute(query)
        return [_to_domain(r) for r in result.scalars().all()]

    async def update(self, model_id: str, **fields) -> ModelSpec:
        result = await self.session.execute(select(ModelORM).where(ModelORM.model_id == model_id))
        row = result.scalar_one_or_none()
        if row is None:
            raise NotFoundError(f"Model '{model_id}' not found.")
        for key, value in fields.items():
            if value is None:
                continue
            if key == "capabilities":
                row.capabilities = [c.value if hasattr(c, "value") else c for c in value]
            elif key in ("cost_metadata", "latency_metadata", "resource_requirements", "reliability_metadata"):
                setattr(row, key, value.model_dump() if hasattr(value, "model_dump") else value)
            elif key == "execution_type":
                row.execution_type = value.value if hasattr(value, "value") else value
            elif key == "metadata":
                row.model_metadata = value
            else:
                setattr(row, key, value)
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def delete(self, model_id: str) -> None:
        result = await self.session.execute(delete(ModelORM).where(ModelORM.model_id == model_id))
        await self.session.commit()
        if result.rowcount == 0:
            raise NotFoundError(f"Model '{model_id}' not found.")
