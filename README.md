# AI Task Manager

A task manager with a web UI and REST API. Type a task in plain English — *"urgent client call Friday at 3pm"* — and GPT-4o mini pulls out the title, due date, and priority automatically. Every task is also auto-categorized on creation.

[![CI](https://github.com/mostafazaghoul/AITaskManager/actions/workflows/ci.yml/badge.svg)](https://github.com/mostafazaghoul/AITaskManager/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- **Smart Add** — press Enter on a plain-English description and the task is created instantly (title, due date, priority inferred by GPT)
- **Auto-categorization** — every task is classified into Work / Personal / Learning / Health / Finance / Home / Other on creation
- **Inline editing** — click the pencil icon on any task to edit it in place
- **Search + filter** — search by keyword, filter by status (All / Active / Done) or category
- **Daily planner** — GPT generates a time-blocked schedule that puts High-priority tasks first
- **Overdue summary** — see all incomplete tasks past their due date at a glance
- **Live stats bar** — completion rate, progress bar, and priority breakdown update on every change
- **Web UI** at `/`, interactive API docs at `/docs`

---

## Quick Start

**Prerequisites:** Python 3.11+, an [OpenAI API key](https://platform.openai.com/api-keys) with billing enabled.

```bash
git clone https://github.com/mostafazaghoul/AITaskManager.git
cd AITaskManager

python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Open .env and set: OPENAI_API_KEY="sk-..."

uvicorn app.main:app --reload
```

Open `http://localhost:8000` for the web UI, or `http://localhost:8000/docs` for the API.

> **Note:** If you don't have an OpenAI key, the app still works — tasks just stay as "Uncategorized" and AI features return an error. All CRUD operations work without a key.

---

## API Reference

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks/` | Create a task (triggers auto-categorization) |
| `GET` | `/tasks/` | List all tasks |
| `GET` | `/tasks/stats` | Completion rate, priority breakdown, category breakdown |
| `GET` | `/tasks/{id}` | Get a single task |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ai/parse` | Parse plain English into structured task fields |
| `GET` | `/ai/plan/daily` | Generate a prioritized daily schedule |
| `GET` | `/ai/summary/overdue` | List overdue incomplete tasks |

**Example — create a task:**

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Read Clean Code", "priority": "High", "due_date": "2026-06-10T09:00:00"}'
```

```json
{
  "id": 1,
  "title": "Read Clean Code",
  "due_date": "2026-06-10T09:00:00",
  "priority": "High",
  "completed": false,
  "category": "Learning",
  "created_at": "2026-06-02T10:22:31"
}
```

**Example — parse natural language:**

```bash
curl -X POST http://localhost:8000/ai/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "urgent client call tomorrow at 3pm"}'
```

```json
{
  "title": "Client call",
  "description": null,
  "due_date": "2026-06-03T15:00:00Z",
  "priority": "High"
}
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11 · FastAPI |
| Database | SQLite (swappable to PostgreSQL via `DATABASE_URL`) |
| ORM | SQLAlchemy 2.x |
| AI | OpenAI API · `gpt-4o-mini` |
| Validation | Pydantic v2 |
| Testing | Pytest · FastAPI `TestClient` · `unittest.mock` |
| Deployment | Docker |

---

## Tests

All OpenAI calls are mocked — no API key needed to run the suite.

```bash
pytest -v
```

```
app/tests/test_ai.py::test_parse_task         PASSED
app/tests/test_ai.py::test_get_daily_plan     PASSED
app/tests/test_ai.py::test_get_overdue_tasks  PASSED
app/tests/test_tasks.py::test_create_task     PASSED
app/tests/test_tasks.py::test_read_tasks      PASSED
app/tests/test_tasks.py::test_update_task     PASSED
app/tests/test_tasks.py::test_delete_task     PASSED
app/tests/test_tasks.py::test_get_stats       PASSED

8 passed
```

---

## Docker

```bash
docker build -t ai-task-manager .
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." ai-task-manager
```

The API key is passed at runtime and never written into the image.
