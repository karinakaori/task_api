from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from .database import TaskDB
from .schemas import TaskCreate, TaskStatus, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task_create: TaskCreate) -> TaskDB:
        task = TaskDB(
            id=str(uuid4()),
            title=task_create.title,
            description=task_create.description,
            status=task_create.status.value,
            created_at=datetime.now(timezone.utc),
            due_date=task_create.due_date,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[TaskStatus] = None,
    ) -> List[TaskDB]:
        query = self.db.query(TaskDB)
        if status is not None:
            query = query.filter(TaskDB.status == status.value)
        return query.order_by(TaskDB.created_at.desc()).offset(skip).limit(limit).all()

    def get(self, task_id: UUID) -> Optional[TaskDB]:
        return self.db.query(TaskDB).filter(TaskDB.id == str(task_id)).first()

    def update(self, task_id: UUID, task_update: TaskUpdate) -> Optional[TaskDB]:
        task = self.get(task_id)
        if not task:
            return None

        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.due_date is not None:
            task.due_date = task_update.due_date
        if task_update.status is not None:
            task.status = task_update.status.value

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: UUID) -> bool:
        task = self.get(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True
