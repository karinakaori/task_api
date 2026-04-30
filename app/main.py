from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple
from uuid import UUID
import logging
import sys
import time

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .crud import TaskRepository
from .database import Base, engine, get_db
from .schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="Task API",
    description="Serviço simples de gerenciamento de tarefas com frontend estático e backend em FastAPI.",
    version="1.0.0",
    lifespan=lifespan,
)

# Diretório que contém os arquivos estáticos do frontend
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configuração de logs estruturados para facilitar análise e depuração.
logger = logging.getLogger("task_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logger.addHandler(handler)

LOGGER_NAME = "task_api"
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60

class SimpleRateLimiter:
    """Middleware de limitação de taxa simples por endereço IP."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, Deque[float]] = {}

    def is_request_allowed(self, client_ip: str) -> Tuple[bool, Optional[int]]:
        now = time.time()
        if client_ip not in self.clients:
            self.clients[client_ip] = deque()

        timestamps = self.clients[client_ip]
        while timestamps and timestamps[0] <= now - self.window_seconds:
            timestamps.popleft()

        if len(timestamps) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - timestamps[0]))
            return False, max(retry_after, 1)

        timestamps.append(now)
        return True, None

rate_limiter = SimpleRateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)

def reset_rate_limiter() -> None:
    """Limpa o estado do rate limiter, usado apenas em testes para isolar requisições."""
    rate_limiter.clients.clear()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = rate_limiter.is_request_allowed(client_ip)
    if not allowed:
        logger.warning("Rate limit excedido para %s", client_ip)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please wait before retrying."},
            headers={"Retry-After": str(retry_after)},
        )
    return await call_next(request)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        "%s %s completed_in=%.2fms status_code=%s",
        request.method,
        request.url.path,
        process_time,
        response.status_code,
    )
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Falha de validação para %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.exception("Erro inesperado em %s %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def get_repository(db: Session) -> TaskRepository:
    """Retorna um repositório de tarefas para operar sobre o banco de dados."""
    return TaskRepository(db)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    """Serve a página principal do frontend."""
    return HTMLResponse(static_dir.joinpath("index.html").read_text(encoding="utf-8"))


def initialize_database() -> None:
    """Cria as tabelas no banco de dados quando a aplicação sobe."""
    Base.metadata.create_all(bind=engine)


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova tarefa",
)
def create_task(task_create: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """Recebe dados de criação e adiciona nova tarefa ao banco."""
    repository = get_repository(db)
    return repository.create(task_create)


@app.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Lista as tarefas existentes",
)
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[TaskStatus] = Query(None),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """Retorna uma lista de tarefas com paginação e filtro de status."""
    repository = get_repository(db)
    return repository.list(skip=skip, limit=limit, status=status)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Busca tarefa pelo ID",
)
def get_task(task_id: UUID, db: Session = Depends(get_db)) -> TaskResponse:
    """Retorna uma tarefa específica ou 404 caso não exista."""
    repository = get_repository(db)
    task = repository.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Atualiza parcialmente uma tarefa",
)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Atualiza os campos enviados de uma tarefa existente."""
    repository = get_repository(db)
    task = repository.update(task_id, task_update)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove uma tarefa",
)
def delete_task(task_id: UUID, db: Session = Depends(get_db)) -> None:
    """Exclui uma tarefa pelo ID."""
    repository = get_repository(db)
    deleted = repository.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None
