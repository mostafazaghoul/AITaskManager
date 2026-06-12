"""AI daily-plan generation via the OpenAI API.

Takes the user's incomplete tasks and produces an encouraging,
time-blocked schedule for the day.
"""
from typing import List

from openai import OpenAIError

from .. import models
from .llm import OPENAI_MODEL, AIServiceError, get_client

# A little creativity makes the plan read naturally.
PLAN_TEMPERATURE: float = 0.7
PLAN_MAX_TOKENS: int = 500

SYSTEM_PROMPT: str = "You are a world-class productivity coach."


def _format_task_list(tasks: List[models.Task]) -> str:
    """Render tasks as a bullet list the model can reason about.

    Args:
        tasks: Tasks to include in the plan.

    Returns:
        One line per task with priority, due date, and category.
    """
    return "\n".join(
        f"- [{task.priority}] {task.title} "
        f"(Due: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'No due date'}, "
        f"Category: {task.category})"
        for task in tasks
    )


def generate_daily_plan(tasks: List[models.Task]) -> str:
    """Generate a prioritized daily schedule for the given tasks.

    Args:
        tasks: Incomplete tasks to schedule.

    Returns:
        The plan as plain text.

    Raises:
        AIServiceError: If the API call fails.
    """
    if not tasks:
        return "No tasks for today! Time to relax or add some new ones."

    prompt = f"""
    You are a productivity expert. Given the following tasks (each tagged with a priority level),
    create a smart, prioritized daily schedule. Schedule High priority tasks during peak morning hours.
    Group related tasks by context (e.g. 'Deep Work', 'Errands', 'Admin'). Suggest a realistic
    timeline and be encouraging.

    Tasks:
    {_format_task_list(tasks)}

    Your suggested plan:
    """

    try:
        response = get_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=PLAN_TEMPERATURE,
            max_tokens=PLAN_MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as exc:
        raise AIServiceError(f"Daily plan generation failed: {exc}") from exc
