"""Execution domain model: the contract between the router's decision and
provider adapters, plus fallback bookkeeping."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStatus(str, enum.Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class ExecutionRequest(BaseModel):
    routing_id: str
    task_id: str
    provider_id: str
    model_id: str
    prompt: str
    max_tokens: int | None = None
    timeout_seconds: float = 30.0
    # The selected candidate's context_window (from RankedCandidate), so
    # adapters can detect an oversized prompt BEFORE calling the provider,
    # and so a provider's own "context length exceeded" error can be
    # normalized to a single ModelForge error code (CONTEXT_LENGTH_EXCEEDED)
    # that the execution service knows how to fall back on intelligently.
    model_context_window: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    output_text: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    latency_ms: int | None = None
    simulated: bool = False


class ExecutionAttempt(BaseModel):
    attempt_id: str = Field(default_factory=lambda: f"attempt_{uuid.uuid4().hex[:12]}")
    routing_id: str
    task_id: str
    attempt_number: int
    provider_id: str
    model_id: str
    result: ExecutionResult
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionHistory(BaseModel):
    task_id: str
    routing_id: str
    attempts: list[ExecutionAttempt] = Field(default_factory=list)
    final_status: ExecutionStatus | None = None
    final_provider_id: str | None = None
    final_model_id: str | None = None
