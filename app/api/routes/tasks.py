from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.repositories.tasks import TaskRepository
from app.schemas.tasks import TaskCreate, TaskListResponse, TaskResponse, TaskStatus, TaskUpdate
from app.services.tasks import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova tarefa",
)
def create_task(
    task_create: TaskCreate,
    service: TaskService = Depends(get_task_service),
    owner_id: str | None = Depends(get_current_user_id),
) -> TaskResponse:
    return service.create(task_create, owner_id=owner_id)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Lista as tarefas existentes",
)
def list_tasks(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    service: TaskService = Depends(get_task_service),
    owner_id: str | None = Depends(get_current_user_id),
) -> TaskListResponse:
    return service.list(skip=skip, limit=limit, status=status_filter, owner_id=owner_id)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Busca tarefa pelo ID",
)
def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
    owner_id: str | None = Depends(get_current_user_id),
) -> TaskResponse:
    task = service.get(task_id, owner_id=owner_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Atualiza parcialmente uma tarefa",
)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    owner_id: str | None = Depends(get_current_user_id),
) -> TaskResponse:
    task = service.update(task_id, task_update, owner_id=owner_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma tarefa",
)
def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
    owner_id: str | None = Depends(get_current_user_id),
) -> None:
    deleted = service.delete(task_id, owner_id=owner_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None
