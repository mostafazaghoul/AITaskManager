"""Application entry point: FastAPI app setup, static UI, and routers."""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import create_database_tables
from .routes import ai, subtasks, tasks

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIR: str = os.path.join(os.path.dirname(__file__), "static")

API_TITLE: str = "AI-Powered To-Do List API"
API_DESCRIPTION: str = (
    "A smart, extensible REST API for managing daily tasks with AI assistance."
)
API_VERSION: str = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run startup tasks: create tables and sanity-check configuration.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to the application for its lifetime.
    """
    create_database_tables()
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning(
            "OPENAI_API_KEY is not set — AI features will be unavailable, "
            "but task CRUD will work normally."
        )
    yield


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    """Serve the single-page web UI.

    Returns:
        The static ``index.html`` file.
    """
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


app.include_router(tasks.router)
app.include_router(subtasks.router)
app.include_router(ai.router)
