"""AI-powered endpoints under ``/ai``: parsing, planning, summaries."""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..services import breakdown, parser, planner
from ..services.llm import AIServiceError

logger = logging.getLogger(__name__)

# Maximum number of tasks fed into the daily planner prompt.
PLANNER_TASK_LIMIT: int = 50

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/parse", response_model=schemas.ParsedTask)
def parse_task(body: schemas.NaturalLanguageInput) -> schemas.ParsedTask:
    """Parse a natural-language string into structured task fields.

    Does not create a task — use ``POST /tasks/`` to save after reviewing.

    Args:
        body: The free-form text to parse.

    Returns:
        The extracted title, description, due date, and priority.

    Raises:
        HTTPException: 502 if the AI service fails.
    """
    try:
        data = parser.parse_task_from_text(body.text)
        return schemas.ParsedTask(**data)
    except AIServiceError as exc:
        logger.error("Parse failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service could not parse this input. Please try again.",
        ) from exc


@router.get("/summary/overdue", response_model=List[schemas.Task])
def get_overdue_summary(db: Session = Depends(get_db)) -> List[schemas.Task]:
    """List all incomplete tasks that are past their due date.

    Args:
        db: Injected database session.

    Returns:
        A list of overdue tasks, possibly empty.
    """
    return crud.get_overdue_tasks(db)


@router.post("/breakdown/{task_id}", response_model=List[schemas.Subtask])
def breakdown_task(task_id: int, db: Session = Depends(get_db)) -> List[schemas.Subtask]:
    """Break a task into actionable subtasks with AI and save them.

    Args:
        task_id: ID of the task to break down.
        db: Injected database session.

    Returns:
        The newly created subtasks.

    Raises:
        HTTPException: 404 if the task does not exist, 502 if the AI
            service fails.
    """
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    try:
        titles = breakdown.generate_subtasks(task.title, task.description)
    except AIServiceError as exc:
        logger.error("Breakdown failed for task %s: %s", task_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service could not break down this task. Please try again.",
        ) from exc

    return [
        crud.create_subtask(db, task_id, schemas.SubtaskCreate(title=title))
        for title in titles
    ]


@router.get("/plan/daily", response_model=schemas.DailyPlanResponse)
def get_daily_plan(db: Session = Depends(get_db)) -> schemas.DailyPlanResponse:
    """Generate a prioritized daily plan from all incomplete tasks.

    Args:
        db: Injected database session.

    Returns:
        The plan as plain text.

    Raises:
        HTTPException: 502 if the AI service fails.
    """
    tasks = crud.get_tasks(db=db, limit=PLANNER_TASK_LIMIT)
    incomplete_tasks = [task for task in tasks if not task.completed]

    if not incomplete_tasks:
        return schemas.DailyPlanResponse(plan="No incomplete tasks to plan. Great job!")

    try:
        plan_text = planner.generate_daily_plan(incomplete_tasks)
    except AIServiceError as exc:
        logger.error("Daily plan generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service could not generate a plan. Please try again.",
        ) from exc

    return schemas.DailyPlanResponse(plan=plan_text)
