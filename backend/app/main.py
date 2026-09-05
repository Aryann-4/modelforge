"""ModelForge Package 1 - FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import complete, execution, models, policies, providers, route_alias, routing, system, tasks
from app.core.config import settings
from app.infrastructure.database.base import init_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield


app = FastAPI(
    title="ModelForge - Core Routing Platform",
    description=(
        "Package 1 prototype: routes tasks to the best eligible AI model across "
        "user-registered providers, enforcing hard policy/privacy/resource "
        "constraints before any soft ranking."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(providers.router)
app.include_router(models.router)
app.include_router(policies.router)
app.include_router(tasks.router)
app.include_router(routing.router)
app.include_router(route_alias.router)
app.include_router(complete.router)
app.include_router(execution.router)
app.include_router(system.router)


@app.get("/")
async def root():
    return {"name": "ModelForge", "package": 1, "docs": "/docs"}
