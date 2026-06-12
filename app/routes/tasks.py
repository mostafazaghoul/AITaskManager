"""Task CRUD endpoints under ``/tasks``."""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..services import categorizer

logger = logging.getLogger(__name__)

# Pagination bounds for task listing.
DEFAULT_PAGE_SIZE: int = 100
MAX_PAGE_SIZE: int = 500

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)) -> schemas.Task:
    """Create a new task and auto-assign a category with AI.

    Args:
        task: Validated creation payload.
        db: Injected database session.

    Returns:
        The created task. If categorization fails the task is still
        created with its default category.
    """
    db_task = crud.create_task(db=db, task=task)

    # Categorization is best-effort: an AI failure must never lose the task.
    try:
        category = categorizer.get_task_category(db_task.title, db_task.description)
        db_task = crud.update_task(
            db=db, task_id=db_task.id, task_update=schemas.TaskUpdate(category=category)
        )
    except Exception:
        logger.exception("Could not categorize task %s", db_task.id)

    return db_task


@router.get("/stats", response_model=schemas.TaskStats)
def get_stats(db: Session = Depends(get_db)) -> schemas.TaskStats:
    """Return aggregate statistics across all tasks.

    Args:
        db: Injected database session.

    Returns:
        Totals, completion rate, and breakdowns by priority and category.
    """
    return crud.get_task_stats(db)


@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(
        DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Page size"
    ),
    db: Session = Depends(get_db),
) -> List[schemas.Task]:
    """List tasks with pagination.

    Args:
        skip: Offset into the result set.
        limit: Maximum number of tasks to return.
        db: Injected database session.

    Returns:
        A list of tasks, possibly empty.
    """
    return crud.get_tasks(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)) -> schemas.Task:
    """Fetch a single task by ID.

    Args:
        task_id: ID of the task to fetch.
        db: Injected database session.

    Returns:
        The matching task.

    Raises:
        HTTPException: 404 if no task with that ID exists.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)
) -> schemas.Task:
    """Partially update an existing task.

    Args:
        task_id: ID of the task to update.
        task: Fields to change; omitted fields are left untouched.
        db: Injected database session.

    Returns:
        The updated task.

    Raises:
        HTTPException: 404 if no task with that ID exists.
    """
    db_task = crud.update_task(db=db, task_id=task_id, task_update=task)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task


@router.delete("/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> schemas.Task:
    """Delete a task and all of its subtasks.

    Args:
        task_id: ID of the task to delete.
        db: Injected database session.

    Returns:
        The task that was deleted.

    Raises:
        HTTPException: 404 if no task with that ID exists.
    """
    db_task = crud.delete_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task
