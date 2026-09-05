from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_routing_service, get_task_service
from app.application.routing_service import RoutingService
from app.application.task_service import TaskService
from app.core.errors import NotFoundError
from app.domain.tasks.models import TaskCreate

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])


class RouteTaskPayload(BaseModel):
    task: TaskCreate
    policy_id: str = "hybrid-default"


@router.post("/route")
async def route_task(
    payload: RouteTaskPayload,
    task_svc: TaskService = Depends(get_task_service),
    routing_svc: RoutingService = Depends(get_routing_service),
):
    task = await task_svc.create(payload.task)
    try:
        decision = await routing_svc.route_task(task, payload.policy_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return {"task": task.model_dump(mode="json"), "decision": decision.model_dump(mode="json")}
