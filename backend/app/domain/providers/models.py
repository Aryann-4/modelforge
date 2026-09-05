"""Provider domain model.

A Provider represents a registered AI backend (user-added or built-in).
The domain layer knows nothing about HTTP, SQLAlchemy, or FastAPI.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProviderType(str, enum.Enum):
    """Supported provider protocol families for Package 1.

    Package 2+ can add new adapters (Anthropic, Gemini, Ollama, vLLM,
    OpenRouter, Groq, Together, ...) without changing this enum's
    consumers, as long as they map to one of these protocol families
    or a new one is added here and given an adapter.
    """

    MOCK = "MOCK"
    OPENAI_COMPATIBLE = "OPENAI_COMPATIBLE"
    LOCAL_HTTP = "LOCAL_HTTP"


class ProviderHealth(str, enum.Enum):
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


def _validate_base_url(v: str | None) -> str | None:
    """Shared base_url validation. `base_url` is legitimately optional (e.g.
    MOCK providers have none), so None is always allowed -- only a
    non-empty, malformed value is rejected."""
    if v is None:
        return v
    if not (v.startswith("http://") or v.startswith("https://")):
        raise ValueError("base_url must start with http:// or https://")
    return v.rstrip("/")


class Provider(BaseModel):
    """A registered AI provider (built-in or user-added).

    `credential_reference` is never a raw secret. It is a lookup key into
    an environment-backed or vault-backed credential store. See
    docs/provider-system.md for the prototype's security limitations.
    """

    provider_id: str
    name: str
    type: ProviderType
    base_url: str | None = None
    credential_reference: str | None = None
    protocol: str = "native"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    health: ProviderHealth = ProviderHealth.UNKNOWN
    last_health_check_at: datetime | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("base_url")
    @classmethod
    def _check_base_url(cls, v: str | None) -> str | None:
        return _validate_base_url(v)

    def is_routable(self) -> bool:
        """A provider can receive routing traffic only if enabled and healthy-or-unknown."""
        return self.enabled and self.health != ProviderHealth.UNHEALTHY


class ProviderCreate(BaseModel):
    provider_id: str
    name: str
    type: ProviderType
    base_url: str | None = None
    credential_reference: str | None = None
    protocol: str = "native"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("base_url")
    @classmethod
    def _check_base_url(cls, v: str | None) -> str | None:
        return _validate_base_url(v)


class ProviderUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    credential_reference: str | None = None
    protocol: str | None = None
    enabled: bool | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("base_url")
    @classmethod
    def _check_base_url(cls, v: str | None) -> str | None:
        return _validate_base_url(v)
