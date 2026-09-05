from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.execution_service import ExecutionService
from app.application.model_service import ModelService
from app.application.policy_service import PolicyService
from app.application.provider_service import ProviderService
from app.application.routing_service import RoutingService
from app.application.task_service import TaskService
from app.core.config import settings
from app.infrastructure.database.base import get_session
from app.infrastructure.repositories.model_repo import ModelRepository
from app.infrastructure.repositories.policy_repo import PolicyRepository
from app.infrastructure.repositories.provider_repo import ProviderRepository
from app.infrastructure.repositories.routing_repo import RoutingRepository
from app.infrastructure.repositories.task_repo import TaskRepository
from app.infrastructure.resources.monitor import RealResourceMonitor, ResourceMonitor


async def get_db(session: AsyncSession = Depends(get_session)) -> AsyncGenerator[AsyncSession, None]:
    yield session


def get_resource_monitor() -> ResourceMonitor:
    return RealResourceMonitor(assumed_vram_gb=settings.assumed_vram_gb, gpu_available=settings.gpu_available)


async def get_provider_service(session: AsyncSession = Depends(get_db)) -> ProviderService:
    return ProviderService(ProviderRepository(session))


async def get_model_service(session: AsyncSession = Depends(get_db)) -> ModelService:
    return ModelService(ModelRepository(session))


async def get_policy_service(session: AsyncSession = Depends(get_db)) -> PolicyService:
    return PolicyService(PolicyRepository(session))


async def get_task_service(session: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(session))


async def get_routing_service(session: AsyncSession = Depends(get_db)) -> RoutingService:
    return RoutingService(
        provider_repo=ProviderRepository(session),
        model_repo=ModelRepository(session),
        policy_repo=PolicyRepository(session),
        routing_repo=RoutingRepository(session),
        resource_monitor=get_resource_monitor(),
    )


async def get_execution_service(
    session: AsyncSession = Depends(get_db),
    provider_service: ProviderService = Depends(get_provider_service),
) -> ExecutionService:
    return ExecutionService(
        provider_repo=ProviderRepository(session),
        routing_repo=RoutingRepository(session),
        provider_service_resolve_credentials=provider_service._resolve_credentials,
        max_attempts=settings.execution_max_attempts,
    )
