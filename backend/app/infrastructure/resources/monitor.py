"""Resource monitoring: a real (psutil-based) snapshot provider and a
deterministic mock snapshot provider for tests/demos.

Both implement the same `ResourceMonitor` protocol so the routing/execution
layers don't care which one is wired up.
"""
from __future__ import annotations

from typing import Protocol

from app.domain.resources.models import ResourceSnapshot


class ResourceMonitor(Protocol):
    def snapshot(self) -> ResourceSnapshot: ...


class RealResourceMonitor:
    """Uses psutil for CPU/RAM. VRAM/GPU are not reliably queryable without
    vendor-specific tooling (nvidia-smi, etc.), so for this prototype they
    default to zero/False unless overridden via environment-configured
    defaults. This is documented as a prototype limitation."""

    def __init__(self, assumed_vram_gb: float = 0.0, gpu_available: bool = False):
        self._assumed_vram_gb = assumed_vram_gb
        self._gpu_available = gpu_available

    def snapshot(self) -> ResourceSnapshot:
        import psutil

        vm = psutil.virtual_memory()
        return ResourceSnapshot(
            cpu_count=psutil.cpu_count(logical=True) or 1,
            cpu_utilization_pct=psutil.cpu_percent(interval=0.05),
            ram_total_gb=round(vm.total / (1024**3), 2),
            ram_available_gb=round(vm.available / (1024**3), 2),
            vram_total_gb=self._assumed_vram_gb,
            vram_available_gb=self._assumed_vram_gb,
            gpu_available=self._gpu_available,
            active_workloads=0,
            source="measured",
        )


class MockResourceMonitor:
    """Deterministic snapshot for tests and demos (e.g. Demo 4: 8GB VRAM
    available, insufficient for a 24GB model)."""

    def __init__(self, snapshot: ResourceSnapshot | None = None):
        self._snapshot = snapshot or ResourceSnapshot(
            cpu_count=8,
            cpu_utilization_pct=20.0,
            ram_total_gb=32.0,
            ram_available_gb=20.0,
            vram_total_gb=8.0,
            vram_available_gb=8.0,
            gpu_available=True,
            active_workloads=0,
            source="mock",
        )

    def snapshot(self) -> ResourceSnapshot:
        return self._snapshot
