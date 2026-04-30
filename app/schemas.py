from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    """Representa os estados válidos de uma tarefa."""
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    """Esquema para criação de novas tarefas."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[date] = None
    status: TaskStatus = Field(default=TaskStatus.todo)

    @field_validator("title")
    def title_must_be_valid(cls, value: str) -> str:
        """Garantir que o título não seja apenas espaços em branco."""
        if not value.strip():
            raise ValueError("title must contain non-whitespace characters")
        return value.strip()


class TaskUpdate(BaseModel):
    """Esquema para atualização parcial de tarefas."""
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    def title_must_be_valid(cls, value: Optional[str]) -> Optional[str]:
        """Garantir que o título atualizado seja válido se fornecido."""
        if value is None:
            return value
        if not value.strip():
            raise ValueError("title must contain non-whitespace characters")
        return value.strip()


class TaskResponse(BaseModel):
    """Esquema usado na resposta da API para enviar os dados da tarefa."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    created_at: datetime
    due_date: Optional[date] = None


class TaskListResponse(BaseModel):
    """Esquema de lista de tarefas, caso seja utilizado no futuro."""
    model_config = ConfigDict(from_attributes=True)

    tasks: list[TaskResponse]
