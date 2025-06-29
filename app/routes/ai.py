# app/routes/ai.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..services import planner

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

@router.get("/summary/overdue", response_model=List[schemas.Task])
def get_overdue_summary(db: Session = Depends(get_db)):
    """
    Get a list of all tasks that are past their due date and not completed.
    """
    overdue_tasks = crud.get_overdue_tasks(db)
    return overdue_tasks

@router.get("/plan/daily", response_model=schemas.DailyPlanResponse)
def get_daily_plan(db: Session = Depends(get_db)):
    """
    Generate a smart daily plan based on all incomplete tasks.
    """
    # Work In Progress: This endpoint will generate a daily plan based on incomplete tasks.
    tasks = crud.get_tasks(db=db, limit=50) # Capping to 50 tasks for the prompt
    incomplete_tasks = [task for task in tasks if not task.completed]

    if not incomplete_tasks:
        return schemas.DailyPlanResponse(plan="No incomplete tasks to plan. Great job!")

    try:
        plan_text = planner.generate_daily_plan(incomplete_tasks)
        return schemas.DailyPlanResponse(plan=plan_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily plan: {e}"
        )