from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.db.models import TaskDB
from app.schemas.tasks import TaskCreate, TaskStatus, TaskUpdate


class TaskRepository:
    """Encapsulates database operations for tasks."""

    def __init__(self, db: Session):
        self.db = db

    def _commit_and_refresh(self, task: TaskDB) -> TaskDB:
        self.db.commit()
        self.db.refresh(task)
        return task

    def create(self, task_create: TaskCreate, owner_id: str | None = None) -> TaskDB:
        task = TaskDB(
            id=str(uuid4()),
            title=task_create.title,
            description=task_create.description,
            status=task_create.status.value,
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
            due_date=task_create.due_date,
        )
        self.db.add(task)
        return self._commit_and_refresh(task)

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[TaskStatus] = None,
        owner_id: str | None = None,
    ) -> list[TaskDB]:
        query = self._base_query(status=status, owner_id=owner_id)
        return query.order_by(TaskDB.created_at.desc()).offset(skip).limit(limit).all()

    def count(self, status: Optional[TaskStatus] = None, owner_id: str | None = None) -> int:
        return self._base_query(status=status, owner_id=owner_id).count()

    def get(self, task_id: UUID, owner_id: str | None = None) -> Optional[TaskDB]:
        query = self.db.query(TaskDB).filter(TaskDB.id == str(task_id))
        if owner_id is not None:
            query = query.filter(TaskDB.owner_id == owner_id)
        return query.first()

    def update(self, task_id: UUID, task_update: TaskUpdate, owner_id: str | None = None) -> Optional[TaskDB]:
        task = self.get(task_id, owner_id=owner_id)
        if not task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                value = value.value
            setattr(task, field, value)

        return self._commit_and_refresh(task)

    def delete(self, task_id: UUID, owner_id: str | None = None) -> bool:
        task = self.get(task_id, owner_id=owner_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def _base_query(self, status: Optional[TaskStatus] = None, owner_id: str | None = None):
        query = self.db.query(TaskDB)
        if status is not None:
            query = query.filter(TaskDB.status == status.value)
        if owner_id is not None:
            query = query.filter(TaskDB.owner_id == owner_id)
        return query
