from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_model_service, get_provider_service
from app.application.model_service import ModelService
from app.application.provider_service import ProviderService
from app.infrastructure.resources.monitor import RealResourceMonitor

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status")
async def system_status(
    provider_svc: ProviderService = Depends(get_provider_service),
    model_svc: ModelService = Depends(get_model_service),
):
    providers = await provider_svc.list()
    models = await model_svc.list()
    snapshot = RealResourceMonitor().snapshot()
    return {
        "provider_count": len(providers),
        "enabled_provider_count": sum(1 for p in providers if p.enabled),
        "model_count": len(models),
        "enabled_model_count": sum(1 for m in models if m.enabled),
        "resource_snapshot": snapshot.model_dump(mode="json"),
    }


@router.get("/health")
async def health():
    return {"status": "ok"}
