"""Generic provider adapter interface.

The routing engine and execution service must never know how a provider
communicates. Every adapter implements this interface; new adapters
(Anthropic, Gemini, Ollama, vLLM, OpenRouter, Groq, Together, custom REST)
plug in here without any routing code changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.execution.models import ExecutionRequest, ExecutionResult
from app.domain.providers.models import Provider, ProviderHealth


class ProviderAdapter(ABC):
    provider: Provider

    def __init__(self, provider: Provider):
        self.provider = provider

    @abstractmethod
    async def health_check(self) -> ProviderHealth: ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        """Return model identifiers the provider currently reports (best-effort discovery)."""

    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult: ...
