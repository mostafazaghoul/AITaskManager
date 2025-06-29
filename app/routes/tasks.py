# app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_db
from ..services import categorizer

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task. The category will be automatically assigned by the AI.
    """
    # First, create the task in the database
    db_task = crud.create_task(db=db, task=task)
    
    # Then, get the AI-powered category
    try:
        category = categorizer.get_task_category(db_task.title, db_task.description)
        # Update the task with the new category
        update_data = schemas.TaskUpdate(category=category)
        db_task = crud.update_task(db=db, task_id=db_task.id, task_update=update_data)
    except Exception as e:
        # If AI categorization fails, we still have the task saved.
        # We can log the error and proceed.
        print(f"Could not categorize task {db_task.id}: {e}")
        # The task will have its default "Uncategorized" value.

    return db_task

@router.get("/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all tasks.
    """
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single task by its ID.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """
    Update an existing task.
    """
    db_task = crud.update_task(db=db, task_id=task_id, task_update=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task.
    """
    db_task = crud.delete_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task