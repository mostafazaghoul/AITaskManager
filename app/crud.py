# app/crud.py
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas
import datetime

# READ a single task by ID
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

# READ multiple tasks
def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

# READ overdue tasks
def get_overdue_tasks(db: Session):
    return db.query(models.Task).filter(
        models.Task.due_date < datetime.datetime.now(datetime.UTC),
        models.Task.completed == False
    ).all()

# STATS
def get_task_stats(db: Session) -> dict:
    total     = db.query(func.count(models.Task.id)).scalar()
    completed = db.query(func.count(models.Task.id)).filter(models.Task.completed == True).scalar()

    by_priority = {
        row[0]: row[1]
        for row in db.query(models.Task.priority, func.count(models.Task.id))
                      .group_by(models.Task.priority).all()
    }
    by_category = {
        row[0]: row[1]
        for row in db.query(models.Task.category, func.count(models.Task.id))
                      .group_by(models.Task.category).all()
    }

    return {
        "total": total,
        "completed": completed,
        "active": total - completed,
        "completion_rate": round(completed / total * 100, 1) if total else 0.0,
        "by_priority": by_priority,
        "by_category": by_category,
    }

# CREATE a new task
def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# UPDATE a task
def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

# DELETE a task
def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task