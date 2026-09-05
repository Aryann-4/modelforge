"""Resource abstraction: what compute is available right now."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ResourceSnapshot(BaseModel):
    """A point-in-time view of available compute.

    `source` distinguishes a real measurement from a deterministic mock
    used in tests/demos -- never claim a mock snapshot is measured.
    """

    cpu_count: int
    cpu_utilization_pct: float
    ram_total_gb: float
    ram_available_gb: float
    vram_total_gb: float
    vram_available_gb: float
    gpu_available: bool
    active_workloads: int = 0
    source: str = "unknown"  # "measured" | "mock"
    taken_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def has_capacity_for(self, required_ram_gb: float, required_vram_gb: float) -> bool:
        if required_ram_gb and self.ram_available_gb < required_ram_gb:
            return False
        if required_vram_gb and self.vram_available_gb < required_vram_gb:
            return False
        return True
