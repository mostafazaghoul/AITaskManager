"""Natural-language task parsing via the OpenAI API.

Turns free-form text like "urgent report due Friday at 3pm" into the
structured fields of a task: title, description, due date, priority.
"""
import datetime
import json

from openai import OpenAIError

from ..constants import DEFAULT_PRIORITY, VALID_PRIORITIES
from .llm import OPENAI_MODEL, AIServiceError, get_client

# Deterministic output is preferred for extraction tasks.
PARSE_TEMPERATURE: float = 0.0
PARSE_MAX_TOKENS: int = 150

# Fallback title length when the model omits one.
FALLBACK_TITLE_LENGTH: int = 100

SYSTEM_PROMPT: str = (
    "You are a task parser. Extract structured task data from natural "
    "language. Return valid JSON only."
)


def _build_prompt(text: str, now: datetime.datetime) -> str:
    """Build the user prompt for the extraction request.

    Args:
        text: The raw natural-language input.
        now: Current UTC time, given to the model so relative dates
            ("tomorrow", "Friday") resolve correctly.

    Returns:
        The fully formatted prompt string.
    """
    return f"""Today is {now.strftime("%A, %B %d, %Y")} and the current time is {now.strftime("%H:%M UTC")}.

Extract task details from the input below and return a JSON object with exactly these keys:
- "title": concise task title (string, required)
- "description": extra context beyond the title, or null if nothing to add
- "due_date": ISO 8601 UTC datetime string if a date/time is mentioned, otherwise null
- "priority": "High", "Medium", or "Low"
  Clues → High: urgent, ASAP, critical, important, deadline
           Low: sometime, whenever, eventually, no rush
           Medium: everything else

Input: "{text}"
"""


def parse_task_from_text(text: str) -> dict:
    """Extract structured task fields from a natural-language string.

    Args:
        text: Plain-English task description.

    Returns:
        A dict with ``title``, ``description``, ``due_date``, and
        ``priority`` keys, sanitized so required fields always exist.

    Raises:
        AIServiceError: If the API call fails or returns unusable JSON.
    """
    now = datetime.datetime.now(datetime.UTC)

    try:
        response = get_client().chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_prompt(text, now)},
            ],
            temperature=PARSE_TEMPERATURE,
            max_tokens=PARSE_MAX_TOKENS,
        )
        data = json.loads(response.choices[0].message.content)
    except (OpenAIError, json.JSONDecodeError) as exc:
        raise AIServiceError(f"Task parsing failed: {exc}") from exc

    # Sanitize so required fields always exist with sensible defaults.
    data.setdefault("title", text[:FALLBACK_TITLE_LENGTH])
    data.setdefault("description", None)
    data.setdefault("due_date", None)
    if data.get("priority") not in VALID_PRIORITIES:
        data["priority"] = DEFAULT_PRIORITY

    return data
