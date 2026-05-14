# app/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
import datetime

# Base schema for a task, contains common attributes
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["Read a book"])
    description: Optional[str] = Field(None, max_length=500, examples=["Read 'Clean Code' for 1 hour."])
    due_date: Optional[datetime.datetime] = None

# Schema for creating a task (doesn't have ID, etc.)
class TaskCreate(TaskBase):
    pass

# Schema for updating a task (all fields are optional)
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime.datetime] = None
    completed: Optional[bool] = None
    category: Optional[str] = None

# Schema for reading a task (includes all database fields)
class Task(TaskBase):
    id: int
    completed: bool
    category: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# Schema for AI-generated daily plan
class DailyPlanResponse(BaseModel):
    plan: str