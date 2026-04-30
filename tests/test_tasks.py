import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

client = TestClient(app)


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    Base.metadata.drop_all(bind=engine)


def test_create_task_success() -> None:
    payload = {"title": "Write integration tests", "description": "Add a few scenarios"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    result = response.json()
    assert result["title"] == payload["title"]
    assert result["description"] == payload["description"]
    assert result["status"] == "todo"
    assert result["due_date"] is None
    assert "id" in result
    assert "created_at" in result


def test_create_task_validation_error() -> None:
    payload = {"title": "Hi"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]


def test_create_task_with_due_date() -> None:
    payload = {"title": "Task with due date", "description": "Deadline test", "due_date": "2026-05-01"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    result = response.json()
    assert result["due_date"] == "2026-05-01"


def test_list_tasks_with_filters_and_pagination() -> None:
    client.post("/tasks", json={"title": "Task A", "description": "First task"})
    client.post("/tasks", json={"title": "Task B", "description": "Second task"})
    client.post("/tasks", json={"title": "Task C", "description": "Third task"})

    response = client.get("/tasks", params={"skip": 0, "limit": 2})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2

    task_id = items[0]["id"]
    update_response = client.put(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert update_response.status_code == 200

    filter_response = client.get("/tasks", params={"status": "in_progress"})
    assert filter_response.status_code == 200
    filtered_items = filter_response.json()
    assert all(item["status"] == "in_progress" for item in filtered_items)


def test_get_task_not_found_returns_404() -> None:
    random_id = str(uuid.uuid4())
    response = client.get(f"/tasks/{random_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
