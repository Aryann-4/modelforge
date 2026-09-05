"""Adapter factory: maps a Provider's declared type to a concrete adapter.

This is the ONLY place that switches on provider type. Everything above it
(routing, execution service, API) works against the generic ProviderAdapter
interface.
"""
from __future__ import annotations

from app.domain.providers.models import Provider, ProviderType
from app.infrastructure.providers.base import ProviderAdapter
from app.infrastructure.providers.mock_adapter import MockProviderAdapter
from app.infrastructure.providers.openai_compatible_adapter import OpenAICompatibleAdapter


def build_adapter(provider: Provider) -> ProviderAdapter:
    if provider.type == ProviderType.MOCK:
        return MockProviderAdapter(provider)
    if provider.type in (ProviderType.OPENAI_COMPATIBLE, ProviderType.LOCAL_HTTP):
        return OpenAICompatibleAdapter(provider)
    raise ValueError(f"No adapter registered for provider type: {provider.type}")
