from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_provider_service
from app.application.provider_service import ProviderService
from app.core.errors import ModelForgeError, NotFoundError
from app.domain.providers.models import Provider, ProviderCreate, ProviderUpdate

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


def _public(provider: Provider) -> dict:
    """Never return credential_reference's resolved secret -- only the
    reference name (a lookup key, not a secret) is exposed."""
    data = provider.model_dump(mode="json")
    data.pop("metadata", None)
    return data


@router.post("", status_code=201)
async def create_provider(payload: ProviderCreate, svc: ProviderService = Depends(get_provider_service)):
    try:
        provider = await svc.create(payload)
    except ModelForgeError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return _public(provider)


@router.get("")
async def list_providers(svc: ProviderService = Depends(get_provider_service)):
    return [_public(p) for p in await svc.list()]


@router.get("/{provider_id}")
async def get_provider(provider_id: str, svc: ProviderService = Depends(get_provider_service)):
    try:
        return _public(await svc.get(provider_id))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc


@router.patch("/{provider_id}")
async def update_provider(
    provider_id: str, payload: ProviderUpdate, svc: ProviderService = Depends(get_provider_service)
):
    try:
        return _public(await svc.update(provider_id, payload))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except ModelForgeError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(provider_id: str, svc: ProviderService = Depends(get_provider_service)):
    try:
        await svc.delete(provider_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc


@router.post("/{provider_id}/health")
async def health_check(provider_id: str, svc: ProviderService = Depends(get_provider_service)):
    try:
        return _public(await svc.health_check(provider_id))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except ModelForgeError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc


@router.post("/{provider_id}/models/discover")
async def discover_models(provider_id: str, svc: ProviderService = Depends(get_provider_service)):
    try:
        return {"provider_id": provider_id, "discovered_model_ids": await svc.discover_models(provider_id)}
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except ModelForgeError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
