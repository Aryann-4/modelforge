"""Exposes POST /api/v1/route as specified in the integration brief, as a
thin alias over /api/v1/routing/route (kept for REST namespace consistency)."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.routing import RouteTaskPayload, route_task

router = APIRouter(prefix="/api/v1", tags=["routing"])
router.add_api_route("/route", route_task, methods=["POST"])
