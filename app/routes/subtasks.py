# app/routes/subtasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/tasks/{task_id}/subtasks", tags=["Subtasks"])

@router.get("/", response_model=List[schemas.Subtask])
def list_subtasks(task_id: int, db: Session = Depends(get_db)):
    if not crud.get_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_subtasks(db, task_id)

@router.post("/", response_model=schemas.Subtask, status_code=status.HTTP_201_CREATED)
def create_subtask(task_id: int, subtask: schemas.SubtaskCreate, db: Session = Depends(get_db)):
    if not crud.get_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.create_subtask(db, task_id, subtask)

@router.put("/{subtask_id}", response_model=schemas.Subtask)
def update_subtask(task_id: int, subtask_id: int, subtask: schemas.SubtaskUpdate, db: Session = Depends(get_db)):
    db_sub = crud.update_subtask(db, subtask_id, subtask)
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return db_sub

@router.delete("/{subtask_id}", response_model=schemas.Subtask)
def delete_subtask(task_id: int, subtask_id: int, db: Session = Depends(get_db)):
    db_sub = crud.delete_subtask(db, subtask_id)
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return db_sub
