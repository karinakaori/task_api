from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[date] = None
    status: TaskStatus = Field(default=TaskStatus.todo)

    @field_validator("title")
    def title_must_be_valid(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("title must contain non-whitespace characters")
        return value.strip()


class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    def title_must_be_valid(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("title must contain non-whitespace characters")
        return value.strip()


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    created_at: datetime
    due_date: Optional[date] = None


class TaskListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tasks: list[TaskResponse]
