# tests/test_tasks.py
from fastapi.testclient import TestClient
from unittest.mock import patch

# We patch the categorizer to avoid making real API calls during tests
@patch('app.services.categorizer.get_task_category', return_value="Work")
def test_create_task(mock_get_category, client: TestClient):
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test description"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test description"
    assert "id" in data
    assert data["completed"] is False
    # Check if the mock was called and the category was set
    assert data["category"] == "Work"
    mock_get_category.assert_called_once()

def test_read_tasks(client: TestClient):
    # Create a task first
    client.post("/tasks/", json={"title": "Task 1", "description": "Desc 1"})
    
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"

def test_update_task(client: TestClient):
    # Create a task
    create_response = client.post("/tasks/", json={"title": "Old Title"})
    task_id = create_response.json()["id"]

    # Update it
    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "New Title", "completed": True}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "New Title"
    assert data["completed"] is True

def test_get_stats(client: TestClient):
    client.post("/tasks/", json={"title": "Task A", "priority": "High"})
    client.post("/tasks/", json={"title": "Task B", "priority": "Low"})
    client.put("/tasks/1", json={"completed": True})

    response = client.get("/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["active"] == 1
    assert data["completion_rate"] == 50.0
    assert data["by_priority"]["High"] == 1
    assert data["by_priority"]["Low"] == 1

def test_delete_task(client: TestClient):
    # Create a task
    create_response = client.post("/tasks/", json={"title": "To be deleted"})
    task_id = create_response.json()["id"]

    # Delete it
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200

    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404