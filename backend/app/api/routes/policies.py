from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_policy_service
from app.application.policy_service import PolicyService
from app.core.errors import NotFoundError
from app.domain.policies.models import PolicyCreate

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])


@router.post("", status_code=201)
async def create_policy(payload: PolicyCreate, svc: PolicyService = Depends(get_policy_service)):
    return (await svc.create(payload)).model_dump(mode="json")


@router.get("")
async def list_policies(svc: PolicyService = Depends(get_policy_service)):
    return [p.model_dump(mode="json") for p in await svc.list()]


@router.get("/{policy_id}")
async def get_policy(policy_id: str, svc: PolicyService = Depends(get_policy_service)):
    try:
        return (await svc.get(policy_id)).model_dump(mode="json")
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
