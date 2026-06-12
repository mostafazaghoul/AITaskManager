"""AI task breakdown via the OpenAI API.

Splits a task into a handful of small, actionable subtask titles.
"""
import json
from typing import List, Optional

from openai import OpenAIError

from .llm import OPENAI_MODEL, AIServiceError, get_client

BREAKDOWN_MAX_TOKENS: int = 300

# How many subtasks the model is asked to produce.
MIN_SUBTASKS: int = 4
MAX_SUBTASKS: int = 6


def generate_subtasks(title: str, description: Optional[str] = None) -> List[str]:
    """Break a task into concise, actionable subtask titles.

    Args:
        title: The parent task title.
        description: Optional extra context for the model.

    Returns:
        A list of subtask title strings (may be empty if the model
        returns none).

    Raises:
        AIServiceError: If the API call fails or returns unusable JSON.
    """
    prompt = (
        f"Break down this task into {MIN_SUBTASKS} to {MAX_SUBTASKS} "
        f'specific, actionable subtasks.\nTask: "{title}"'
    )
    if description:
        prompt += f"\nContext: {description}"
    prompt += (
        '\nReturn a JSON object with a single key "subtasks" containing '
        "an array of concise subtask title strings."
    )

    try:
        response = get_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=BREAKDOWN_MAX_TOKENS,
        )
        data = json.loads(response.choices[0].message.content)
    except (OpenAIError, json.JSONDecodeError) as exc:
        raise AIServiceError(f"Task breakdown failed: {exc}") from exc

    return [str(item) for item in data.get("subtasks", [])]
