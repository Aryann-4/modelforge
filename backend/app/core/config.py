"""Application configuration via environment variables.

For the prototype, database credentials and provider API keys are read from
the environment (or a .env file loaded by python-dotenv). See
docs/provider-system.md for security limitations of this approach.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MODELFORGE_", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./modelforge.db"
    log_level: str = "INFO"
    log_full_prompts: bool = False  # if False, prompts are truncated/redacted in logs
    assumed_vram_gb: float = 0.0
    gpu_available: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    # Used by POST /api/v1/complete when the caller doesn't specify a
    # policy_id -- lets the "just answer this" endpoint be fully hands-off.
    # Must match a policy_id that actually exists (app.seed creates it).
    default_policy_id: str = "hybrid-default"
    default_privacy_classification: str = "INTERNAL"
    execution_max_attempts: int = 3


settings = Settings()
