# tests/test_ai.py
from fastapi.testclient import TestClient
from unittest.mock import patch

@patch('app.services.planner.generate_daily_plan')
def test_get_daily_plan(mock_generate_plan, client: TestClient):
    # Mock the return value of the AI planner
    mock_plan = "1. Do the test. 2. Celebrate."
    mock_generate_plan.return_value = mock_plan

    # Create a task so the list isn't empty
    client.post("/tasks/", json={"title": "Write a test", "description": "Test the daily planner"})

    response = client.get("/ai/plan/daily")
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == mock_plan
    # Check that our service was called
    mock_generate_plan.assert_called_once()