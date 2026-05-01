import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.tasks import router as tasks_router
from app.core.config import get_settings
from app.core.errors import (
    error_response,
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.core.rate_limit import SimpleRateLimiter
from app.db.database import Base, engine
from app.db import models


settings = get_settings()
logger = configure_logging()
rate_limiter = SimpleRateLimiter(settings.rate_limit_max_requests, settings.rate_limit_window_seconds)
static_dir = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.include_router(tasks_router)


def reset_rate_limiter() -> None:
    rate_limiter.reset()


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/static"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = rate_limiter.is_request_allowed(client_ip)
    if not allowed:
        logger.warning("rate_limit_exceeded", extra={"client_ip": client_ip, "path": request.url.path})
        return error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please wait before retrying.",
            headers={"Retry-After": str(retry_after)},
        )

    return await call_next(request)


app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    return HTMLResponse(static_dir.joinpath("index.html").read_text(encoding="utf-8"))


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
