# app/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
import datetime

VALID_PRIORITIES = ["High", "Medium", "Low"]

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["Read a book"])
    description: Optional[str] = Field(None, max_length=500, examples=["Read 'Clean Code' for 1 hour."])
    due_date: Optional[datetime.datetime] = None
    priority: str = Field("Medium", examples=["Medium"])

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime.datetime] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    category: Optional[str] = None

class Task(TaskBase):
    id: int
    completed: bool
    priority: str
    category: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class DailyPlanResponse(BaseModel):
    plan: str

# Task statistics
class TaskStats(BaseModel):
    total: int
    completed: int
    active: int
    completion_rate: float
    by_priority: dict
    by_category: dict

# Natural language parsing
class NaturalLanguageInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, examples=["Meet with team tomorrow at 9am"])

class ParsedTask(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    priority: str = "Medium"

# Subtasks
class SubtaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Write the introduction"])

class SubtaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    completed: Optional[bool] = None

class Subtask(BaseModel):
    id: int
    task_id: int
    title: str
    completed: bool
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)
