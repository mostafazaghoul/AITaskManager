# app/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .database import create_database_tables
from .routes import tasks, ai, subtasks
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create database tables on startup
create_database_tables()

_STATIC = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(
    title="AI-Powered To-Do List API",
    description="A smart, extensible REST API for managing daily tasks with AI assistance.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=_STATIC), name="static")

@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse(os.path.join(_STATIC, "index.html"))

# Include routers
app.include_router(tasks.router)
app.include_router(subtasks.router)
app.include_router(ai.router)

# Basic check for OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable not found.")
    print("AI features will not work.")