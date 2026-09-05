from __future__ import annotations

import os
from datetime import datetime, timezone

from app.core.errors import ProviderConfigurationError
from app.core.logging import log_event
from app.domain.providers.models import Provider, ProviderCreate, ProviderHealth, ProviderUpdate
from app.infrastructure.providers.registry import build_adapter
from app.infrastructure.repositories.provider_repo import ProviderRepository


class ProviderService:
    def __init__(self, repo: ProviderRepository):
        self.repo = repo

    async def create(self, payload: ProviderCreate) -> Provider:
        self._validate(payload.base_url, payload.credential_reference)
        provider = Provider(**payload.model_dump())
        created = await self.repo.add(provider)
        log_event("PROVIDER_CREATED", provider_id=created.provider_id, type=created.type.value)
        return created

    async def get(self, provider_id: str) -> Provider:
        return await self.repo.get(provider_id)

    async def list(self) -> list[Provider]:
        return await self.repo.list()

    async def update(self, provider_id: str, payload: ProviderUpdate) -> Provider:
        self._validate(payload.base_url, payload.credential_reference)
        updated = await self.repo.update(provider_id, **payload.model_dump(exclude_unset=True))
        log_event("PROVIDER_UPDATED", provider_id=provider_id)
        return updated

    async def delete(self, provider_id: str) -> None:
        await self.repo.delete(provider_id)
        log_event("PROVIDER_DELETED", provider_id=provider_id)

    async def health_check(self, provider_id: str) -> Provider:
        provider = await self.repo.get(provider_id)
        provider = self._resolve_credentials(provider)
        adapter = build_adapter(provider)
        health = await adapter.health_check()
        updated = await self.repo.set_health(provider_id, health, datetime.now(timezone.utc))
        log_event("PROVIDER_HEALTH_CHECKED", provider_id=provider_id, health=health.value)
        return updated

    async def discover_models(self, provider_id: str) -> list[str]:
        provider = await self.repo.get(provider_id)
        provider = self._resolve_credentials(provider)
        adapter = build_adapter(provider)
        return await adapter.list_models()

    def _validate(self, base_url: str | None, credential_reference: str | None) -> None:
        # Pydantic already validates the URL scheme; this is where additional
        # prototype-level checks (e.g. private-network guards) would go.
        return None

    def _resolve_credentials(self, provider: Provider) -> Provider:
        """Resolve credential_reference -> actual secret via environment variable.

        PROTOTYPE LIMITATION: secrets are read from process environment
        variables named after `credential_reference`. This is documented in
        docs/provider-system.md as not production-grade secret storage.
        """
        if provider.credential_reference:
            resolved = os.environ.get(provider.credential_reference)
            if resolved is None:
                raise ProviderConfigurationError(
                    f"Credential reference '{provider.credential_reference}' not found in environment."
                )
            provider = provider.model_copy(update={"metadata": {**provider.metadata, "_resolved_api_key": resolved}})
        return provider
