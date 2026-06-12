"""SQLAlchemy ORM models for tasks and their subtasks."""
import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .constants import DEFAULT_CATEGORY, DEFAULT_PRIORITY
from .database import Base


def _utc_now() -> datetime.datetime:
    """Return the current UTC time, used as the ``created_at`` default."""
    return datetime.datetime.now(datetime.UTC)


class Task(Base):
    """A single to-do item, optionally broken down into subtasks."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default=DEFAULT_PRIORITY)
    category = Column(String, default=DEFAULT_CATEGORY)
    created_at = Column(DateTime, default=_utc_now)

    subtasks = relationship(
        "Subtask", back_populates="task", cascade="all, delete-orphan"
    )


class Subtask(Base):
    """A small actionable step belonging to a parent task."""

    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utc_now)

    task = relationship("Task", back_populates="subtasks")
