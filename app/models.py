# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base
import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="Medium")
    category = Column(String, default="Uncategorized")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))