"""Subtask CRUD endpoints nested under ``/tasks/{task_id}/subtasks``."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/tasks/{task_id}/subtasks", tags=["Subtasks"])


def _ensure_task_exists(db: Session, task_id: int) -> None:
    """Raise a 404 if the parent task does not exist.

    Args:
        db: Active database session.
        task_id: ID of the parent task.

    Returns:
        None.

    Raises:
        HTTPException: 404 if the task is missing.
    """
    if not crud.get_task(db, task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )


@router.get("/", response_model=List[schemas.Subtask])
def list_subtasks(task_id: int, db: Session = Depends(get_db)) -> List[schemas.Subtask]:
    """List all subtasks of a task, oldest first.

    Args:
        task_id: ID of the parent task.
        db: Injected database session.

    Returns:
        A list of subtasks, possibly empty.

    Raises:
        HTTPException: 404 if the parent task does not exist.
    """
    _ensure_task_exists(db, task_id)
    return crud.get_subtasks(db, task_id)


@router.post("/", response_model=schemas.Subtask, status_code=status.HTTP_201_CREATED)
def create_subtask(
    task_id: int, subtask: schemas.SubtaskCreate, db: Session = Depends(get_db)
) -> schemas.Subtask:
    """Add a subtask to a task.

    Args:
        task_id: ID of the parent task.
        subtask: Validated creation payload.
        db: Injected database session.

    Returns:
        The created subtask.

    Raises:
        HTTPException: 404 if the parent task does not exist.
    """
    _ensure_task_exists(db, task_id)
    return crud.create_subtask(db, task_id, subtask)


@router.put("/{subtask_id}", response_model=schemas.Subtask)
def update_subtask(
    task_id: int,
    subtask_id: int,
    subtask: schemas.SubtaskUpdate,
    db: Session = Depends(get_db),
) -> schemas.Subtask:
    """Partially update a subtask.

    Args:
        task_id: ID of the parent task (path consistency only).
        subtask_id: ID of the subtask to update.
        subtask: Fields to change; omitted fields are left untouched.
        db: Injected database session.

    Returns:
        The updated subtask.

    Raises:
        HTTPException: 404 if no subtask with that ID exists.
    """
    db_sub = crud.update_subtask(db, subtask_id, subtask)
    if not db_sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found"
        )
    return db_sub


@router.delete("/{subtask_id}", response_model=schemas.Subtask)
def delete_subtask(
    task_id: int, subtask_id: int, db: Session = Depends(get_db)
) -> schemas.Subtask:
    """Delete a subtask.

    Args:
        task_id: ID of the parent task (path consistency only).
        subtask_id: ID of the subtask to delete.
        db: Injected database session.

    Returns:
        The subtask that was deleted.

    Raises:
        HTTPException: 404 if no subtask with that ID exists.
    """
    db_sub = crud.delete_subtask(db, subtask_id)
    if not db_sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found"
        )
    return db_sub
