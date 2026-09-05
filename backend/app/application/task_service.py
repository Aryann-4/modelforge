from __future__ import annotations

from app.core.logging import log_event
from app.domain.tasks.models import RuleBasedTaskClassifier, Task, TaskClassifier, TaskCreate
from app.infrastructure.repositories.task_repo import TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository, classifier: TaskClassifier | None = None):
        self.repo = repo
        self.classifier = classifier or RuleBasedTaskClassifier()

    async def create(self, payload: TaskCreate) -> Task:
        if payload.task_type is not None and payload.requirements is not None:
            task_type, requirements = payload.task_type, payload.requirements
        else:
            classified_type, classified_reqs = self.classifier.classify(payload.user_request)
            task_type = payload.task_type or classified_type
            requirements = payload.requirements or classified_reqs

        task = Task(
            user_request=payload.user_request,
            task_type=task_type,
            requirements=requirements,
            privacy_classification=payload.privacy_classification,
            policy_id=payload.policy_id,
            priority=payload.priority,
            metadata=payload.metadata,
        )
        created = await self.repo.add(task)
        log_event(
            "TASK_CREATED",
            task_id=created.task_id,
            task_type=created.task_type.value,
            privacy_classification=created.privacy_classification.value,
            classifier=self.classifier.name if hasattr(self.classifier, "name") else "custom",
        )
        return created

    async def get(self, task_id: str) -> Task:
        return await self.repo.get(task_id)
