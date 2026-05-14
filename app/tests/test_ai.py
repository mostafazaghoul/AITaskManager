# tests/test_ai.py
from fastapi.testclient import TestClient
from unittest.mock import patch

@patch('app.services.planner.generate_daily_plan')
def test_get_daily_plan(mock_generate_plan, client: TestClient):
    mock_plan = "1. Do the test. 2. Celebrate."
    mock_generate_plan.return_value = mock_plan

    client.post("/tasks/", json={"title": "Write a test", "description": "Test the daily planner"})

    response = client.get("/ai/plan/daily")
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == mock_plan
    mock_generate_plan.assert_called_once()


@patch('app.services.parser.parse_task_from_text')
def test_parse_task(mock_parse, client: TestClient):
    mock_parse.return_value = {
        "title": "Meet xyz",
        "description": None,
        "due_date": "2025-06-01T21:00:00+00:00",
        "priority": "High",
    }

    response = client.post("/ai/parse", json={"text": "meet xyz tomorrow at 9pm, urgent"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Meet xyz"
    assert data["priority"] == "High"
    assert data["due_date"] is not None
    mock_parse.assert_called_once_with("meet xyz tomorrow at 9pm, urgent")


def test_get_overdue_tasks(client: TestClient):
    response = client.get("/ai/summary/overdue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
