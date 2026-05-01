import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app, reset_rate_limiter


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    reset_rate_limiter()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    reset_rate_limiter()


def test_create_task_success(client: TestClient) -> None:
    payload = {"title": "Write integration tests", "description": "Add a few scenarios"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    result = response.json()
    assert result["title"] == payload["title"]
    assert result["description"] == payload["description"]
    assert result["status"] == "todo"
    assert result["due_date"] is None
    assert result["owner_id"] is None
    assert "id" in result
    assert "created_at" in result


def test_create_task_validation_error(client: TestClient) -> None:
    payload = {"title": "Hi"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_task_with_due_date(client: TestClient) -> None:
    payload = {"title": "Task with due date", "description": "Deadline test", "due_date": "2026-05-01"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    result = response.json()
    assert result["due_date"] == "2026-05-01"


def test_list_tasks_with_filters_and_pagination(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Task A", "description": "First task"})
    client.post("/tasks", json={"title": "Task B", "description": "Second task"})
    client.post("/tasks", json={"title": "Task C", "description": "Third task"})

    response = client.get("/tasks", params={"skip": 0, "limit": 2})
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 3
    assert page["skip"] == 0
    assert page["limit"] == 2
    assert len(page["items"]) == 2

    task_id = page["items"][0]["id"]
    update_response = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert update_response.status_code == 200

    filter_response = client.get("/tasks", params={"status": "in_progress"})
    assert filter_response.status_code == 200
    filtered_items = filter_response.json()["items"]
    assert all(item["status"] == "in_progress" for item in filtered_items)


def test_get_task_not_found_returns_404(client: TestClient) -> None:
    random_id = str(uuid.uuid4())
    response = client.get(f"/tasks/{random_id}")

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Task not found"


def test_tasks_can_be_scoped_by_future_user_header(client: TestClient) -> None:
    first = client.post("/tasks", headers={"X-User-Id": "user-1"}, json={"title": "Private task"})
    second = client.post("/tasks", headers={"X-User-Id": "user-2"}, json={"title": "Other task"})

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get("/tasks", headers={"X-User-Id": "user-1"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["owner_id"] == "user-1"


def test_rate_limit_blocks_after_too_many_requests(client: TestClient) -> None:
    reset_rate_limiter()

    for _ in range(30):
        response = client.get("/tasks")
        assert response.status_code == 200

    response = client.get("/tasks")
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in response.headers
