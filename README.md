# AI-Powered To-Do List API

A smart REST API for managing daily tasks with AI-assisted categorization and daily planning. Built with Python, FastAPI, SQLAlchemy, and the OpenAI API.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## How It Works

The app is a standard REST API with two layers of intelligence sitting on top of basic task management:

### 1. AI Categorization (on every task creation)

When you `POST /tasks/`, the API does two things in sequence:

1. Saves the task to the SQLite database.
2. Sends the task title and description to **GPT-4o mini** with a prompt asking it to pick one of seven predefined categories (`Work`, `Personal`, `Learning`, `Health`, `Finance`, `Home`, `Other`). The response is a single word — cheap and fast. The task record is then updated with that category.

If the AI call fails for any reason (no key, quota exceeded, network error), the task is still saved with the default `Uncategorized` label — the AI is an enhancement, not a hard dependency.

### 2. Smart Daily Planner (`GET /ai/plan/daily`)

This endpoint fetches all your incomplete tasks (up to 50), formats them into a prompt, and sends them to **GPT-4o mini** with instructions to act as a productivity coach. The model groups tasks by context (e.g. "Deep Work", "Errands"), suggests a realistic timeline, and returns the plan as plain text.

### Architecture

The codebase is split into distinct layers so each piece has one job:

```
app/
├── main.py          # FastAPI app setup, router registration
├── database.py      # SQLAlchemy engine and session management
├── models.py        # SQLAlchemy ORM models (database schema)
├── schemas.py       # Pydantic models (request/response validation)
├── crud.py          # Database queries (no business logic here)
├── routes/
│   ├── tasks.py     # Task CRUD endpoints
│   └── ai.py        # AI-powered endpoints
└── services/
    ├── categorizer.py   # OpenAI call for category classification
    └── planner.py       # OpenAI call for daily plan generation
```

A request flows like this:

```
HTTP Request → Route → (Service for AI logic) → CRUD → Database
                   ↓
             HTTP Response ← Pydantic schema validation
```

---

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks/` | Create a task (auto-categorized by AI) |
| `GET` | `/tasks/` | List all tasks |
| `GET` | `/tasks/{id}` | Get a single task |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

### AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ai/plan/daily` | Generate a prioritized daily plan from all incomplete tasks |
| `GET` | `/ai/summary/overdue` | List all tasks past their due date |

**Example — create a task:**

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Read Clean Code", "description": "Chapter 3 on functions", "due_date": "2025-06-01T09:00:00"}'
```

```json
{
  "id": 1,
  "title": "Read Clean Code",
  "description": "Chapter 3 on functions",
  "due_date": "2025-06-01T09:00:00",
  "completed": false,
  "category": "Learning",
  "created_at": "2025-05-14T10:22:31.004"
}
```

**Example — generate a daily plan:**

```bash
curl http://127.0.0.1:8000/ai/plan/daily
```

```json
{
  "plan": "Good morning! Here's your plan for today...\n\n**Deep Work Block (9am–12pm)**\n..."
}
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ + FastAPI |
| Database | SQLite (dev) — swappable to PostgreSQL via `DATABASE_URL` env var |
| ORM | SQLAlchemy 2.x |
| AI | OpenAI API — `gpt-4o-mini` for both categorization and planning |
| Validation | Pydantic v2 |
| Testing | Pytest + FastAPI `TestClient` + `unittest.mock` |
| Deployment | Docker |

---

## Getting Started

### Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys) with billing enabled

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/mostafazaghoul/AITaskManager.git
cd AITaskManager

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# Edit .env and replace the placeholder with your real key
```

`.env`:
```
OPENAI_API_KEY="sk-..."
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

The API is now running at `http://127.0.0.1:8000`.
Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## Running Tests

Tests mock all OpenAI calls so no API key is needed.

```bash
pytest -v
```

```
app/tests/test_ai.py::test_get_daily_plan     PASSED
app/tests/test_tasks.py::test_create_task     PASSED
app/tests/test_tasks.py::test_read_tasks      PASSED
app/tests/test_tasks.py::test_update_task     PASSED
app/tests/test_tasks.py::test_delete_task     PASSED

5 passed in 8.92s
```

---

## Docker

```bash
docker build -t ai-task-manager .

# Pass the API key at runtime — never bake it into the image
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." ai-task-manager
```

---

## Project Goals

This project was built to demonstrate:

- **Layered backend architecture** — routes, services, CRUD, and models are kept separate and each have a single responsibility.
- **Practical LLM integration** — using an AI model as a backend service rather than a chatbot, with graceful fallback when the API is unavailable.
- **Clean API design** — consistent response shapes, proper HTTP status codes, and automatic interactive documentation via FastAPI.
- **Testable code** — external services are mocked at the boundary so the test suite runs fast and without any real API calls.
- **Production habits** — secrets managed via environment variables, `.env` excluded from version control and Docker images.
