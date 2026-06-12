"""Automatic task categorization via the OpenAI API.

Assigns each new task to one of a fixed set of categories based on its
title and description. Failures fall back to the default category so
task creation never breaks because of an AI hiccup.
"""
import logging
from typing import Optional

from ..constants import DEFAULT_CATEGORY, FALLBACK_CATEGORY, VALID_CATEGORIES
from .llm import OPENAI_MODEL, get_client

logger = logging.getLogger(__name__)

# Deterministic, single-word answer expected.
CATEGORIZE_TEMPERATURE: float = 0.0
CATEGORIZE_MAX_TOKENS: int = 10

SYSTEM_PROMPT: str = "You are an expert task organizer."


def get_task_category(title: str, description: Optional[str] = None) -> str:
    """Classify a task into one of the valid categories.

    Args:
        title: The task title.
        description: Optional extra context.

    Returns:
        One of ``VALID_CATEGORIES``, or ``DEFAULT_CATEGORY`` if the API
        call fails for any reason.
    """
    prompt = f"""
    Categorize the following task into one of the following categories: {', '.join(VALID_CATEGORIES)}.
    Respond with only the category name.

    Task Title: "{title}"
    Task Description: "{description or 'No description'}"

    Category:
    """

    try:
        response = get_client().chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=CATEGORIZE_TEMPERATURE,
            max_tokens=CATEGORIZE_MAX_TOKENS,
        )
        category = response.choices[0].message.content.strip()
        # Guard against the model inventing a category of its own.
        return category if category in VALID_CATEGORIES else FALLBACK_CATEGORY
    except Exception:
        logger.exception("Categorization failed for task %r", title)
        return DEFAULT_CATEGORY
