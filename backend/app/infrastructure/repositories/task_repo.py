from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domain.tasks.models import PrivacyClassification, Task, TaskRequirements, TaskType
from app.infrastructure.database.orm import TaskORM


def _to_domain(row: TaskORM) -> Task:
    return Task(
        task_id=row.task_id,
        user_request=row.user_request,
        task_type=TaskType(row.task_type),
        requirements=TaskRequirements(**(row.requirements or {})),
        privacy_classification=PrivacyClassification(row.privacy_classification),
        policy_id=row.policy_id,
        priority=row.priority,
        metadata=row.task_metadata or {},
        created_at=row.created_at,
    )


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task: Task) -> Task:
        row = TaskORM(
            task_id=task.task_id,
            user_request=task.user_request,
            task_type=task.task_type.value,
            requirements=task.requirements.model_dump(mode="json"),
            privacy_classification=task.privacy_classification.value,
            policy_id=task.policy_id,
            priority=task.priority,
            task_metadata=task.metadata,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _to_domain(row)

    async def get(self, task_id: str) -> Task:
        row = await self.session.get(TaskORM, task_id)
        if row is None:
            raise NotFoundError(f"Task '{task_id}' not found.")
        return _to_domain(row)
