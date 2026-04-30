from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .crud import TaskRepository
from .database import Base, engine, get_db
from .schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title="Task API",
    description="A clean architecture FastAPI service for managing to-do tasks.",
    version="1.0.0",
)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    return HTMLResponse(static_dir.joinpath("index.html").read_text(encoding="utf-8"))


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(task_create: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    repository = TaskRepository(db)
    task = repository.create(task_create)
    return task


@app.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="List existing tasks",
)
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[TaskStatus] = Query(None),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    repository = TaskRepository(db)
    tasks = repository.list(skip=skip, limit=limit, status=status)
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Retrieve a task by ID",
)
def get_task(task_id: UUID, db: Session = Depends(get_db)) -> TaskResponse:
    repository = TaskRepository(db)
    task = repository.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task partially",
)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    repository = TaskRepository(db)
    task = repository.update(task_id, task_update)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(task_id: UUID, db: Session = Depends(get_db)) -> None:
    repository = TaskRepository(db)
    deleted = repository.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None
