"""Normalized ModelForge error types."""
from __future__ import annotations


class ModelForgeError(Exception):
    code: str = "MODELFORGE_ERROR"

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class NotFoundError(ModelForgeError):
    code = "NOT_FOUND"


class ConflictError(ModelForgeError):
    code = "CONFLICT"


class ValidationError(ModelForgeError):
    code = "VALIDATION_ERROR"


class ProviderConfigurationError(ModelForgeError):
    code = "PROVIDER_CONFIGURATION_ERROR"
