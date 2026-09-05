"""Model registry domain model."""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Capability(str, enum.Enum):
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    TOOL_USE = "tool_use"
    STRUCTURED_OUTPUT = "structured_output"
    LONG_CONTEXT = "long_context"


class ExecutionType(str, enum.Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"


class CostMetadata(BaseModel):
    """Cost figures are always estimates configured by whoever registers the model,
    never claimed as real-time billing data."""

    estimated_input_cost_per_1k: float = 0.0
    estimated_output_cost_per_1k: float = 0.0
    currency: str = "USD"
    basis: str = "estimated"  # estimated | measured | unknown


class LatencyMetadata(BaseModel):
    estimated_latency_ms: int = 0
    basis: str = "estimated"  # estimated | measured | unknown


class ResourceRequirements(BaseModel):
    required_vram_gb: float = 0.0
    required_ram_gb: float = 0.0


class ReliabilityMetadata(BaseModel):
    """Reliability is manually configured for this prototype -- there is no
    live SLA feed. `configured_success_rate` is a operator-entered value in [0, 1]."""

    configured_success_rate: float = 0.99
    basis: str = "configured"


class ModelSpec(BaseModel):
    model_id: str
    provider_id: str
    display_name: str

    capabilities: set[Capability] = Field(default_factory=set)

    context_window: int = 8192
    max_output_tokens: int = 2048

    supports_streaming: bool = False
    supports_tools: bool = False
    supports_vision: bool = False

    execution_type: ExecutionType = ExecutionType.CLOUD

    cost_metadata: CostMetadata = Field(default_factory=CostMetadata)
    latency_metadata: LatencyMetadata = Field(default_factory=LatencyMetadata)
    resource_requirements: ResourceRequirements = Field(default_factory=ResourceRequirements)
    reliability_metadata: ReliabilityMetadata = Field(default_factory=ReliabilityMetadata)

    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def has_capability(self, capability: Capability) -> bool:
        return capability in self.capabilities


class ModelCreate(BaseModel):
    model_id: str
    provider_id: str
    display_name: str
    capabilities: set[Capability] = Field(default_factory=set)
    context_window: int = 8192
    max_output_tokens: int = 2048
    supports_streaming: bool = False
    supports_tools: bool = False
    supports_vision: bool = False
    execution_type: ExecutionType = ExecutionType.CLOUD
    cost_metadata: CostMetadata = Field(default_factory=CostMetadata)
    latency_metadata: LatencyMetadata = Field(default_factory=LatencyMetadata)
    resource_requirements: ResourceRequirements = Field(default_factory=ResourceRequirements)
    reliability_metadata: ReliabilityMetadata = Field(default_factory=ReliabilityMetadata)
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelUpdate(BaseModel):
    display_name: str | None = None
    capabilities: set[Capability] | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    supports_streaming: bool | None = None
    supports_tools: bool | None = None
    supports_vision: bool | None = None
    execution_type: ExecutionType | None = None
    cost_metadata: CostMetadata | None = None
    latency_metadata: LatencyMetadata | None = None
    resource_requirements: ResourceRequirements | None = None
    reliability_metadata: ReliabilityMetadata | None = None
    enabled: bool | None = None
    metadata: dict[str, Any] | None = None
