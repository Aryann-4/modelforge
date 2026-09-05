"""Policy domain model.

Policies express hard constraints (things that make a model *ineligible*)
plus soft preferences used only after eligibility filtering. See
app.domain.routing.engine for how these are enforced as two separate
stages -- this separation is a deliberate architectural requirement.
"""
from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field

from app.domain.models.models import Capability
from app.domain.tasks.models import PrivacyClassification


class PolicyPreset(str, enum.Enum):
    SOVEREIGN = "SOVEREIGN"  # local only, no cloud egress at all
    HYBRID = "HYBRID"  # local preferred, cloud allowed for public/internal
    CLOUD = "CLOUD"  # cloud preferred/allowed broadly
    ECONOMY = "ECONOMY"  # optimize for lowest cost among eligible models
    CUSTOM = "CUSTOM"


class Policy(BaseModel):
    policy_id: str
    name: str
    preset: PolicyPreset = PolicyPreset.CUSTOM

    allow_local: bool = True
    allow_cloud: bool = True

    allowed_providers: set[str] = Field(default_factory=set)  # empty == no allowlist restriction
    denied_providers: set[str] = Field(default_factory=set)

    maximum_cost_per_1k: float | None = None
    maximum_latency_ms: int | None = None

    required_capabilities: set[Capability] = Field(default_factory=set)

    allowed_privacy_levels: set[PrivacyClassification] = Field(
        default_factory=lambda: set(PrivacyClassification)
    )

    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyCreate(BaseModel):
    policy_id: str
    name: str
    preset: PolicyPreset = PolicyPreset.CUSTOM
    allow_local: bool = True
    allow_cloud: bool = True
    allowed_providers: set[str] = Field(default_factory=set)
    denied_providers: set[str] = Field(default_factory=set)
    maximum_cost_per_1k: float | None = None
    maximum_latency_ms: int | None = None
    required_capabilities: set[Capability] = Field(default_factory=set)
    allowed_privacy_levels: set[PrivacyClassification] = Field(
        default_factory=lambda: set(PrivacyClassification)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


def preset_policy(preset: PolicyPreset, policy_id: str, name: str) -> Policy:
    """Build one of the four built-in preset policies. Presets are just
    sensible starting points -- the Policy model remains fully extensible."""

    if preset == PolicyPreset.SOVEREIGN:
        return Policy(
            policy_id=policy_id, name=name, preset=preset,
            allow_local=True, allow_cloud=False,
        )
    if preset == PolicyPreset.HYBRID:
        return Policy(
            policy_id=policy_id, name=name, preset=preset,
            allow_local=True, allow_cloud=True,
            allowed_privacy_levels={
                PrivacyClassification.PUBLIC,
                PrivacyClassification.INTERNAL,
            },
        )
    if preset == PolicyPreset.CLOUD:
        return Policy(
            policy_id=policy_id, name=name, preset=preset,
            allow_local=False, allow_cloud=True,
        )
    if preset == PolicyPreset.ECONOMY:
        return Policy(
            policy_id=policy_id, name=name, preset=preset,
            allow_local=True, allow_cloud=True,
            maximum_cost_per_1k=0.5,
        )
    return Policy(policy_id=policy_id, name=name, preset=PolicyPreset.CUSTOM)
