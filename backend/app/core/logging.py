"""Structured logging for routing/execution lifecycle events.

Never logs API keys. Full user prompts are redacted unless
MODELFORGE_LOG_FULL_PROMPTS=true is explicitly set (development only).
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings

logger = logging.getLogger("modelforge")
logger.setLevel(settings.log_level)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(message)s"))
if not logger.handlers:
    logger.addHandler(_handler)

_REDACT_KEYS = {"api_key", "credential_reference", "authorization", "_resolved_api_key"}


def _redact(payload: dict[str, Any]) -> dict[str, Any]:
    clean = {}
    for k, v in payload.items():
        if k.lower() in _REDACT_KEYS:
            clean[k] = "***REDACTED***"
        elif k == "user_request" and not settings.log_full_prompts:
            clean[k] = (v[:80] + "...") if isinstance(v, str) and len(v) > 80 else v
        else:
            clean[k] = v
    return clean


def log_event(event: str, **fields: Any) -> None:
    record = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **_redact(fields),
    }
    logger.info(json.dumps(record, default=str))
