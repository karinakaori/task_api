from uuid import UUID

from app.db.models import TaskDB
from app.repositories.tasks import TaskRepository
from app.schemas.tasks import TaskCreate, TaskListResponse, TaskStatus, TaskUpdate


class TaskService:
    """Coordinates task business rules and persistence."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create(self, task_create: TaskCreate, owner_id: str | None = None) -> TaskDB:
        return self.repository.create(task_create, owner_id=owner_id)

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        status: TaskStatus | None = None,
        owner_id: str | None = None,
    ) -> TaskListResponse:
        items = self.repository.list(skip=skip, limit=limit, status=status, owner_id=owner_id)
        total = self.repository.count(status=status, owner_id=owner_id)
        return TaskListResponse(items=items, total=total, skip=skip, limit=limit)

    def get(self, task_id: UUID, owner_id: str | None = None) -> TaskDB | None:
        return self.repository.get(task_id, owner_id=owner_id)

    def update(self, task_id: UUID, task_update: TaskUpdate, owner_id: str | None = None) -> TaskDB | None:
        return self.repository.update(task_id, task_update, owner_id=owner_id)

    def delete(self, task_id: UUID, owner_id: str | None = None) -> bool:
        return self.repository.delete(task_id, owner_id=owner_id)
