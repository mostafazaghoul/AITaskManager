"""Pydantic schemas defining the request and response shapes of the API."""
import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from .constants import DEFAULT_PRIORITY, Priority

# Field length limits, mirrored by the UI.
TITLE_MAX_LENGTH: int = 100
DESCRIPTION_MAX_LENGTH: int = 500
SUBTASK_TITLE_MAX_LENGTH: int = 200
NL_INPUT_MAX_LENGTH: int = 500


# ── Tasks ─────────────────────────────────────────────────────────────────────

class TaskBase(BaseModel):
    """Fields shared by task creation and task responses."""

    title: str = Field(
        ..., min_length=1, max_length=TITLE_MAX_LENGTH, examples=["Read a book"]
    )
    description: Optional[str] = Field(
        None,
        max_length=DESCRIPTION_MAX_LENGTH,
        examples=["Read 'Clean Code' for 1 hour."],
    )
    due_date: Optional[datetime.datetime] = None
    priority: Priority = Field(DEFAULT_PRIORITY, examples=[DEFAULT_PRIORITY])


class TaskCreate(TaskBase):
    """Payload for creating a new task."""


class TaskUpdate(BaseModel):
    """Partial-update payload; only the provided fields are changed."""

    title: Optional[str] = Field(None, min_length=1, max_length=TITLE_MAX_LENGTH)
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    due_date: Optional[datetime.datetime] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    category: Optional[str] = None


class Task(TaskBase):
    """A task as returned by the API."""

    id: int
    completed: bool
    category: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ── Statistics ────────────────────────────────────────────────────────────────

class TaskStats(BaseModel):
    """Aggregate counters across all tasks."""

    total: int
    completed: int
    active: int
    completion_rate: float
    by_priority: Dict[str, int]
    by_category: Dict[str, int]


# ── AI features ───────────────────────────────────────────────────────────────

class DailyPlanResponse(BaseModel):
    """The AI-generated daily schedule as plain text."""

    plan: str


class NaturalLanguageInput(BaseModel):
    """Free-form text describing a task in plain English."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=NL_INPUT_MAX_LENGTH,
        examples=["Meet with team tomorrow at 9am"],
    )


class ParsedTask(BaseModel):
    """Structured task fields extracted from natural language."""

    title: str
    description: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    priority: Priority = DEFAULT_PRIORITY


# ── Subtasks ──────────────────────────────────────────────────────────────────

class SubtaskCreate(BaseModel):
    """Payload for adding a subtask to a task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=SUBTASK_TITLE_MAX_LENGTH,
        examples=["Write the introduction"],
    )


class SubtaskUpdate(BaseModel):
    """Partial-update payload for a subtask."""

    title: Optional[str] = Field(None, min_length=1, max_length=SUBTASK_TITLE_MAX_LENGTH)
    completed: Optional[bool] = None


class Subtask(BaseModel):
    """A subtask as returned by the API."""

    id: int
    task_id: int
    title: str
    completed: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
