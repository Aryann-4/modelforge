"""Task domain model + a deterministic, rule-based task classifier.

IMPORTANT: The classifier below is intentionally simple and keyword-driven.
It is NOT machine learning and makes no such claim. The interface
(`TaskClassifier.classify`) is designed so a smarter classifier can be
substituted in Package 2 without touching callers.
"""
from __future__ import annotations

import enum
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.domain.models.models import Capability


class TaskType(str, enum.Enum):
    GENERAL = "GENERAL"
    REASONING = "REASONING"
    CODING = "CODING"
    VISION = "VISION"
    DOCUMENT_ANALYSIS = "DOCUMENT_ANALYSIS"
    RAG = "RAG"
    AGENTIC = "AGENTIC"


class PrivacyClassification(str, enum.Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class TaskRequirements(BaseModel):
    """Hard/soft requirements derived from the task, used during eligibility filtering."""

    required_capabilities: set[Capability] = Field(default_factory=set)
    min_context_window: int = 0
    max_estimated_cost_per_1k: float | None = None
    max_estimated_latency_ms: int | None = None


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    user_request: str
    task_type: TaskType = TaskType.GENERAL
    requirements: TaskRequirements = Field(default_factory=TaskRequirements)
    privacy_classification: PrivacyClassification = PrivacyClassification.INTERNAL
    policy_id: str | None = None
    priority: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskCreate(BaseModel):
    user_request: str
    task_type: TaskType | None = None  # None => auto-classify
    requirements: TaskRequirements | None = None
    privacy_classification: PrivacyClassification = PrivacyClassification.INTERNAL
    policy_id: str | None = None
    priority: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskClassifier(Protocol):
    def classify(self, user_request: str) -> tuple[TaskType, TaskRequirements]: ...


_CODING_PATTERNS = re.compile(
    r"\b(code|python|javascript|typescript|function|algorithm|bug|refactor|"
    r"compile|stack trace|regex|sql query|unit test|api endpoint)\b",
    re.IGNORECASE,
)
_VISION_PATTERNS = re.compile(
    r"\b(image|photo|picture|screenshot|diagram|chart|visual|see this|attached image)\b",
    re.IGNORECASE,
)
_DOCUMENT_PATTERNS = re.compile(
    r"\b(document|pdf|contract|report|paper|spreadsheet|invoice|transcript)\b",
    re.IGNORECASE,
)
_RAG_PATTERNS = re.compile(
    r"\b(knowledge base|retrieve|search our docs|lookup in|cite sources|rag)\b",
    re.IGNORECASE,
)
_AGENTIC_PATTERNS = re.compile(
    r"\b(agent|multi-step|autonomously|use tools|orchestrate|execute a plan)\b",
    re.IGNORECASE,
)
_REASONING_PATTERNS = re.compile(
    r"\b(reason|prove|solve|logic|step by step|derive|math problem)\b",
    re.IGNORECASE,
)


class RuleBasedTaskClassifier:
    """Deterministic, keyword/regex-based classifier.

    This explicitly is NOT an ML classifier. It exists to give Package 1 a
    working, explainable default. Replace via the TaskClassifier protocol.
    """

    name = "rule_based_classifier_v1"

    def classify(self, user_request: str) -> tuple[TaskType, TaskRequirements]:
        text = user_request or ""

        if _AGENTIC_PATTERNS.search(text):
            return TaskType.AGENTIC, TaskRequirements(
                required_capabilities={Capability.TOOL_USE}
            )
        if _VISION_PATTERNS.search(text):
            return TaskType.VISION, TaskRequirements(
                required_capabilities={Capability.VISION}
            )
        if _CODING_PATTERNS.search(text):
            return TaskType.CODING, TaskRequirements(
                required_capabilities={Capability.CODING}
            )
        if _RAG_PATTERNS.search(text):
            return TaskType.RAG, TaskRequirements(
                required_capabilities={Capability.LONG_CONTEXT}
            )
        if _DOCUMENT_PATTERNS.search(text):
            return TaskType.DOCUMENT_ANALYSIS, TaskRequirements(
                required_capabilities={Capability.LONG_CONTEXT}
            )
        if _REASONING_PATTERNS.search(text):
            return TaskType.REASONING, TaskRequirements(
                required_capabilities={Capability.REASONING}
            )
        return TaskType.GENERAL, TaskRequirements()
