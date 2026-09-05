"""Routing decision structures.

These are the stable, serializable objects Package 2 depends on. They must
not leak SQLAlchemy or FastAPI details.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ExclusionReason(BaseModel):
    code: str  # e.g. "CLOUD_PROHIBITED", "MISSING_CAPABILITY", "INSUFFICIENT_CONTEXT"
    message: str


class ExcludedCandidate(BaseModel):
    provider_id: str
    model_id: str
    reasons: list[ExclusionReason]


class ScoreBreakdown(BaseModel):
    capability_score: float
    cost_score: float
    latency_score: float
    reliability_score: float
    resource_score: float
    preference_score: float
    total_score: float


class RankedCandidate(BaseModel):
    provider_id: str
    model_id: str
    context_window: int
    score: ScoreBreakdown
    satisfied_reasons: list[str]


class RoutingRequest(BaseModel):
    """Input to the routing engine -- provider-independent."""

    task_id: str
    user_request: str
    task_type: str
    required_capabilities: set[str] = Field(default_factory=set)
    min_context_window: int = 0
    max_estimated_cost_per_1k: float | None = None
    max_estimated_latency_ms: int | None = None
    privacy_classification: str
    policy_id: str


class RoutingDecision(BaseModel):
    routing_id: str = Field(default_factory=lambda: f"route_{uuid.uuid4().hex[:12]}")
    task_id: str

    selected_provider_id: str | None
    selected_model_id: str | None

    candidate_models: list[RankedCandidate]
    excluded_candidates: list[ExcludedCandidate]

    selection_score: float | None

    decision_reasons: list[str]

    policy_applied: str

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_successful(self) -> bool:
        return self.selected_model_id is not None
