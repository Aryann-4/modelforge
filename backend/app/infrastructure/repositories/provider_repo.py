from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domain.providers.models import Provider, ProviderHealth, ProviderType
from app.infrastructure.database.orm import ProviderORM


def _to_domain(row: ProviderORM) -> Provider:
    return Provider(
        provider_id=row.provider_id,
        name=row.name,
        type=ProviderType(row.type),
        base_url=row.base_url,
        credential_reference=row.credential_reference,
        protocol=row.protocol,
        enabled=row.enabled,
        metadata=row.provider_metadata or {},
        health=ProviderHealth(row.health),
        last_health_check_at=row.last_health_check_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class ProviderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, provider: Provider) -> Provider:
        row = ProviderORM(
            provider_id=provider.provider_id,
            name=provider.name,
            type=provider.type.value,
            base_url=provider.base_url,
            credential_reference=provider.credential_reference,
            protocol=provider.protocol,
            enabled=provider.enabled,
            health=provider.health.value,
            provider_metadata=provider.metadata,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def get(self, provider_id: str) -> Provider:
        row = await self.session.get(ProviderORM, provider_id)
        if row is None:
            raise NotFoundError(f"Provider '{provider_id}' not found.")
        return _to_domain(row)

    async def list(self) -> list[Provider]:
        result = await self.session.execute(select(ProviderORM))
        return [_to_domain(r) for r in result.scalars().all()]

    async def update(self, provider_id: str, **fields) -> Provider:
        row = await self.session.get(ProviderORM, provider_id)
        if row is None:
            raise NotFoundError(f"Provider '{provider_id}' not found.")
        for key, value in fields.items():
            if value is None:
                continue
            if key == "metadata":
                row.provider_metadata = value
            else:
                setattr(row, key, value)
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def set_health(self, provider_id: str, health: ProviderHealth, checked_at) -> Provider:
        row = await self.session.get(ProviderORM, provider_id)
        if row is None:
            raise NotFoundError(f"Provider '{provider_id}' not found.")
        row.health = health.value
        row.last_health_check_at = checked_at
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def delete(self, provider_id: str) -> None:
        result = await self.session.execute(
            delete(ProviderORM).where(ProviderORM.provider_id == provider_id)
        )
        await self.session.commit()
        if result.rowcount == 0:
            raise NotFoundError(f"Provider '{provider_id}' not found.")
