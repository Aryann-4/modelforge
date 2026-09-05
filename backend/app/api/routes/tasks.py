from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_task_service
from app.application.task_service import TaskService
from app.core.errors import NotFoundError
from app.domain.tasks.models import TaskCreate

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("", status_code=201)
async def create_task(payload: TaskCreate, svc: TaskService = Depends(get_task_service)):
    return (await svc.create(payload)).model_dump(mode="json")


@router.get("/{task_id}")
async def get_task(task_id: str, svc: TaskService = Depends(get_task_service)):
    try:
        return (await svc.get(task_id)).model_dump(mode="json")
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
