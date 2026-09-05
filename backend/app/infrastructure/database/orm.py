"""SQLAlchemy ORM tables. Deliberately minimal: providers, models, policies,
tasks, routing_decisions, execution_attempts -- nothing more."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProviderORM(Base):
    __tablename__ = "providers"

    provider_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    type: Mapped[str] = mapped_column(String(64))
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    credential_reference: Mapped[str | None] = mapped_column(String(256), nullable=True)
    protocol: Mapped[str] = mapped_column(String(64), default="native")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    health: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    last_health_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    models: Mapped[list["ModelORM"]] = relationship(back_populates="provider", cascade="all, delete-orphan")


class ModelORM(Base):
    __tablename__ = "models"

    model_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    provider_id: Mapped[str] = mapped_column(ForeignKey("providers.provider_id"), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(256))
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    context_window: Mapped[int] = mapped_column(Integer, default=8192)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    supports_streaming: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_tools: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_vision: Mapped[bool] = mapped_column(Boolean, default=False)
    execution_type: Mapped[str] = mapped_column(String(32), default="CLOUD")
    cost_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    latency_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    resource_requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    reliability_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    model_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    provider: Mapped[ProviderORM] = relationship(back_populates="models")


class PolicyORM(Base):
    __tablename__ = "policies"

    policy_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    preset: Mapped[str] = mapped_column(String(32), default="CUSTOM")
    allow_local: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_cloud: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_providers: Mapped[list] = mapped_column(JSON, default=list)
    denied_providers: Mapped[list] = mapped_column(JSON, default=list)
    maximum_cost_per_1k: Mapped[float | None] = mapped_column(Float, nullable=True)
    maximum_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_capabilities: Mapped[list] = mapped_column(JSON, default=list)
    allowed_privacy_levels: Mapped[list] = mapped_column(JSON, default=list)
    policy_metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class TaskORM(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_request: Mapped[str] = mapped_column(Text)
    task_type: Mapped[str] = mapped_column(String(32))
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    privacy_classification: Mapped[str] = mapped_column(String(32))
    policy_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    task_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RoutingDecisionORM(Base):
    __tablename__ = "routing_decisions"

    routing_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(128))
    selected_provider_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    selected_model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    candidate_models: Mapped[list] = mapped_column(JSON, default=list)
    excluded_candidates: Mapped[list] = mapped_column(JSON, default=list)
    selection_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision_reasons: Mapped[list] = mapped_column(JSON, default=list)
    policy_applied: Mapped[str] = mapped_column(String(128))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExecutionAttemptORM(Base):
    __tablename__ = "execution_attempts"

    attempt_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    routing_id: Mapped[str] = mapped_column(String(128))
    task_id: Mapped[str] = mapped_column(String(128))
    attempt_number: Mapped[int] = mapped_column(Integer)
    provider_id: Mapped[str] = mapped_column(String(128))
    model_id: Mapped[str] = mapped_column(String(128))
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
