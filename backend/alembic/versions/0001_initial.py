"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-30
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "providers",
        sa.Column("provider_id", sa.String(128), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("base_url", sa.String(512), nullable=True),
        sa.Column("credential_reference", sa.String(256), nullable=True),
        sa.Column("protocol", sa.String(64), nullable=False, server_default="native"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("health", sa.String(32), nullable=False, server_default="UNKNOWN"),
        sa.Column("last_health_check_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "models",
        sa.Column("model_id", sa.String(128), primary_key=True),
        sa.Column("provider_id", sa.String(128), sa.ForeignKey("providers.provider_id"), primary_key=True),
        sa.Column("display_name", sa.String(256), nullable=False),
        sa.Column("capabilities", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("context_window", sa.Integer, nullable=False, server_default="8192"),
        sa.Column("max_output_tokens", sa.Integer, nullable=False, server_default="2048"),
        sa.Column("supports_streaming", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("supports_tools", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("supports_vision", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("execution_type", sa.String(32), nullable=False, server_default="CLOUD"),
        sa.Column("cost_metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("latency_metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("resource_requirements", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("reliability_metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("model_metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "policies",
        sa.Column("policy_id", sa.String(128), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("preset", sa.String(32), nullable=False, server_default="CUSTOM"),
        sa.Column("allow_local", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("allow_cloud", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("allowed_providers", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("denied_providers", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("maximum_cost_per_1k", sa.Float, nullable=True),
        sa.Column("maximum_latency_ms", sa.Integer, nullable=True),
        sa.Column("required_capabilities", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("allowed_privacy_levels", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("policy_metadata", sa.JSON, nullable=False, server_default="{}"),
    )
    op.create_table(
        "tasks",
        sa.Column("task_id", sa.String(128), primary_key=True),
        sa.Column("user_request", sa.Text, nullable=False),
        sa.Column("task_type", sa.String(32), nullable=False),
        sa.Column("requirements", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("privacy_classification", sa.String(32), nullable=False),
        sa.Column("policy_id", sa.String(128), nullable=True),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("task_metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "routing_decisions",
        sa.Column("routing_id", sa.String(128), primary_key=True),
        sa.Column("task_id", sa.String(128), nullable=False),
        sa.Column("selected_provider_id", sa.String(128), nullable=True),
        sa.Column("selected_model_id", sa.String(128), nullable=True),
        sa.Column("candidate_models", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("excluded_candidates", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("selection_score", sa.Float, nullable=True),
        sa.Column("decision_reasons", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("policy_applied", sa.String(128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "execution_attempts",
        sa.Column("attempt_id", sa.String(128), primary_key=True),
        sa.Column("routing_id", sa.String(128), nullable=False),
        sa.Column("task_id", sa.String(128), nullable=False),
        sa.Column("attempt_number", sa.Integer, nullable=False),
        sa.Column("provider_id", sa.String(128), nullable=False),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("result", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("execution_attempts")
    op.drop_table("routing_decisions")
    op.drop_table("tasks")
    op.drop_table("policies")
    op.drop_table("models")
    op.drop_table("providers")
