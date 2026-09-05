from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_model_service
from app.application.model_service import ModelService
from app.core.errors import ModelForgeError, NotFoundError
from app.domain.models.models import ModelCreate, ModelUpdate

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.post("", status_code=201)
async def create_model(payload: ModelCreate, svc: ModelService = Depends(get_model_service)):
    try:
        return (await svc.create(payload)).model_dump(mode="json")
    except ModelForgeError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc


@router.get("")
async def list_models(provider_id: str | None = None, svc: ModelService = Depends(get_model_service)):
    return [m.model_dump(mode="json") for m in await svc.list(provider_id=provider_id)]


@router.get("/{model_id}")
async def get_model(model_id: str, svc: ModelService = Depends(get_model_service)):
    try:
        return (await svc.get(model_id)).model_dump(mode="json")
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc


@router.patch("/{model_id}")
async def update_model(model_id: str, payload: ModelUpdate, svc: ModelService = Depends(get_model_service)):
    try:
        return (await svc.update(model_id, payload)).model_dump(mode="json")
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc


@router.delete("/{model_id}", status_code=204)
async def delete_model(model_id: str, svc: ModelService = Depends(get_model_service)):
    try:
        await svc.delete(model_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
