import uuid

import pytest
from fastapi.testclient import TestClient

from tests.test_tasks import client


def test_created_task_can_be_retrieved_by_returned_id(client: TestClient) -> None:
    create_response = client.post(
        "/tasks",
        json={"title": "Retrieve persisted task", "description": "Created through the API"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id
    assert get_response.json()["title"] == "Retrieve persisted task"


def test_updated_status_is_persisted_and_returned_on_later_get(client: TestClient) -> None:
    create_response = client.post("/tasks", json={"title": "Update task status"})
    task_id = create_response.json()["id"]

    update_response = client.put(f"/tasks/{task_id}", json={"status": "done"})

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "done"

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "done"


def test_list_filters_and_pagination_return_the_expected_subset(client: TestClient) -> None:
    created_ids = []
    for title, task_status in [
        ("First todo task", "todo"),
        ("Task in progress", "in_progress"),
        ("Completed task", "done"),
    ]:
        response = client.post("/tasks", json={"title": title, "status": task_status})
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    first_page = client.get("/tasks", params={"skip": 0, "limit": 1})
    second_page = client.get("/tasks", params={"skip": 1, "limit": 1})
    done_tasks = client.get("/tasks", params={"status": "done"})

    assert first_page.status_code == 200
    assert first_page.json()["total"] == 3
    assert first_page.json()["skip"] == 0
    assert first_page.json()["limit"] == 1
    assert first_page.json()["items"][0]["id"] in created_ids
    assert second_page.status_code == 200
    assert second_page.json()["items"][0]["id"] != first_page.json()["items"][0]["id"]
    assert done_tasks.status_code == 200
    assert done_tasks.json()["total"] == 1
    assert [task["status"] for task in done_tasks.json()["items"]] == ["done"]


def test_deleted_task_is_no_longer_available(client: TestClient) -> None:
    create_response = client.post("/tasks", json={"title": "Delete persisted task"})
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")

    assert delete_response.status_code == 204
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
    assert get_response.json()["error"]["code"] == "NOT_FOUND"


def test_user_cannot_read_or_update_another_users_task(client: TestClient) -> None:
    owner_headers = {"X-User-Id": "owner-a"}
    other_headers = {"X-User-Id": "owner-b"}
    create_response = client.post("/tasks", headers=owner_headers, json={"title": "Owner A task"})
    task_id = create_response.json()["id"]

    assert client.get(f"/tasks/{task_id}", headers=other_headers).status_code == 404
    assert client.put(f"/tasks/{task_id}", headers=other_headers, json={"status": "done"}).status_code == 404

    owner_response = client.get(f"/tasks/{task_id}", headers=owner_headers)
    assert owner_response.status_code == 200
    assert owner_response.json()["status"] == "todo"


@pytest.mark.parametrize(
    ("payload", "case"),
    [
        ({"description": "Missing title"}, "missing required title"),
        ({"title": "Invalid date", "due_date": "2026-20-40"}, "invalid date"),
        ({"title": "Invalid status", "status": "blocked"}, "unsupported status"),
    ],
)
def test_invalid_create_payload_is_rejected_without_creating_task(
    client: TestClient, payload: dict[str, str], case: str
) -> None:
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422, case
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert client.get("/tasks").json()["total"] == 0


@pytest.mark.parametrize("params", [{"skip": -1}, {"limit": 101}])
def test_invalid_pagination_parameters_are_rejected(client: TestClient, params: dict[str, int]) -> None:
    response = client.get("/tasks", params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_malformed_uuid_is_rejected_by_the_api_contract(client: TestClient) -> None:
    response = client.get("/tasks/not-a-uuid")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_deleting_a_nonexistent_task_returns_not_found(client: TestClient) -> None:
    response = client.delete(f"/tasks/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
