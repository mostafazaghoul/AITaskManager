"""Database access layer: all task and subtask queries live here.

Routes never touch the ORM directly; they call these functions so that
query logic stays in one place and is easy to test.
"""
import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas

# Percentage values are rounded to one decimal place for display.
COMPLETION_RATE_DECIMALS: int = 1


# ── Tasks ─────────────────────────────────────────────────────────────────────

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Fetch a single task by primary key.

    Args:
        db: Active database session.
        task_id: ID of the task to fetch.

    Returns:
        The matching ``Task``, or ``None`` if it does not exist.
    """
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
    """Fetch a page of tasks.

    Args:
        db: Active database session.
        skip: Number of rows to skip (pagination offset).
        limit: Maximum number of rows to return.

    Returns:
        A list of tasks, possibly empty.
    """
    return db.query(models.Task).offset(skip).limit(limit).all()


def get_overdue_tasks(db: Session) -> List[models.Task]:
    """Fetch all incomplete tasks whose due date is in the past.

    Args:
        db: Active database session.

    Returns:
        A list of overdue tasks, possibly empty.
    """
    return (
        db.query(models.Task)
        .filter(
            models.Task.due_date < datetime.datetime.now(datetime.UTC),
            models.Task.completed == False,  # noqa: E712 — SQLAlchemy expression
        )
        .all()
    )


def get_task_stats(db: Session) -> dict:
    """Compute aggregate task statistics.

    Args:
        db: Active database session.

    Returns:
        A dict with ``total``, ``completed``, ``active``,
        ``completion_rate`` (percentage), and per-priority /
        per-category breakdowns.
    """
    total = db.query(func.count(models.Task.id)).scalar() or 0
    completed = (
        db.query(func.count(models.Task.id))
        .filter(models.Task.completed == True)  # noqa: E712 — SQLAlchemy expression
        .scalar()
        or 0
    )

    by_priority = {
        priority: count
        for priority, count in db.query(
            models.Task.priority, func.count(models.Task.id)
        ).group_by(models.Task.priority)
    }
    by_category = {
        category: count
        for category, count in db.query(
            models.Task.category, func.count(models.Task.id)
        ).group_by(models.Task.category)
    }

    completion_rate = (
        round(completed / total * 100, COMPLETION_RATE_DECIMALS) if total else 0.0
    )

    return {
        "total": total,
        "completed": completed,
        "active": total - completed,
        "completion_rate": completion_rate,
        "by_priority": by_priority,
        "by_category": by_category,
    }


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Insert a new task.

    Args:
        db: Active database session.
        task: Validated creation payload.

    Returns:
        The persisted ``Task`` with its generated ID.
    """
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(
    db: Session, task_id: int, task_update: schemas.TaskUpdate
) -> Optional[models.Task]:
    """Apply a partial update to an existing task.

    Args:
        db: Active database session.
        task_id: ID of the task to update.
        task_update: Fields to change; unset fields are left untouched.

    Returns:
        The updated ``Task``, or ``None`` if it does not exist.
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Delete a task (and, via cascade, its subtasks).

    Args:
        db: Active database session.
        task_id: ID of the task to delete.

    Returns:
        The deleted ``Task``, or ``None`` if it does not exist.
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task


# ── Subtasks ──────────────────────────────────────────────────────────────────

def get_subtask(db: Session, subtask_id: int) -> Optional[models.Subtask]:
    """Fetch a single subtask by primary key.

    Args:
        db: Active database session.
        subtask_id: ID of the subtask to fetch.

    Returns:
        The matching ``Subtask``, or ``None`` if it does not exist.
    """
    return db.query(models.Subtask).filter(models.Subtask.id == subtask_id).first()


def get_subtasks(db: Session, task_id: int) -> List[models.Subtask]:
    """Fetch all subtasks of a task, oldest first.

    Args:
        db: Active database session.
        task_id: ID of the parent task.

    Returns:
        A list of subtasks, possibly empty.
    """
    return (
        db.query(models.Subtask)
        .filter(models.Subtask.task_id == task_id)
        .order_by(models.Subtask.created_at)
        .all()
    )


def create_subtask(
    db: Session, task_id: int, subtask: schemas.SubtaskCreate
) -> models.Subtask:
    """Insert a new subtask under a task.

    Args:
        db: Active database session.
        task_id: ID of the parent task.
        subtask: Validated creation payload.

    Returns:
        The persisted ``Subtask`` with its generated ID.
    """
    db_sub = models.Subtask(task_id=task_id, **subtask.model_dump())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def update_subtask(
    db: Session, subtask_id: int, subtask_update: schemas.SubtaskUpdate
) -> Optional[models.Subtask]:
    """Apply a partial update to an existing subtask.

    Args:
        db: Active database session.
        subtask_id: ID of the subtask to update.
        subtask_update: Fields to change; unset fields are left untouched.

    Returns:
        The updated ``Subtask``, or ``None`` if it does not exist.
    """
    db_sub = get_subtask(db, subtask_id)
    if not db_sub:
        return None

    for key, value in subtask_update.model_dump(exclude_unset=True).items():
        setattr(db_sub, key, value)

    db.commit()
    db.refresh(db_sub)
    return db_sub


def delete_subtask(db: Session, subtask_id: int) -> Optional[models.Subtask]:
    """Delete a subtask.

    Args:
        db: Active database session.
        subtask_id: ID of the subtask to delete.

    Returns:
        The deleted ``Subtask``, or ``None`` if it does not exist.
    """
    db_sub = get_subtask(db, subtask_id)
    if not db_sub:
        return None
    db.delete(db_sub)
    db.commit()
    return db_sub
