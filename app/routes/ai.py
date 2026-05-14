# app/routes/ai.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..services import planner, parser

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

@router.post("/parse", response_model=schemas.ParsedTask)
def parse_task(body: schemas.NaturalLanguageInput):
    """
    Parse a natural language string and return structured task fields.
    Does not create a task — use POST /tasks/ to save after reviewing.
    """
    try:
        data = parser.parse_task_from_text(body.text)
        return schemas.ParsedTask(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not parse task: {e}",
        )

@router.get("/summary/overdue", response_model=List[schemas.Task])
def get_overdue_summary(db: Session = Depends(get_db)):
    """
    Get all tasks that are past their due date and not completed.
    """
    return crud.get_overdue_tasks(db)

@router.get("/plan/daily", response_model=schemas.DailyPlanResponse)
def get_daily_plan(db: Session = Depends(get_db)):
    """
    Generate a prioritized daily plan from all incomplete tasks.
    """
    tasks = crud.get_tasks(db=db, limit=50)
    incomplete_tasks = [t for t in tasks if not t.completed]

    if not incomplete_tasks:
        return schemas.DailyPlanResponse(plan="No incomplete tasks to plan. Great job!")

    try:
        plan_text = planner.generate_daily_plan(incomplete_tasks)
        return schemas.DailyPlanResponse(plan=plan_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily plan: {e}",
        )
