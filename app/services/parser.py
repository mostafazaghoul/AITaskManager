# app/services/parser.py
import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_PRIORITIES = ["High", "Medium", "Low"]

def parse_task_from_text(text: str) -> dict:
    """
    Uses GPT-4o-mini to extract title, description, due_date, and priority
    from a natural language string. Returns a plain dict.
    """
    now = datetime.datetime.now(datetime.UTC)

    user_prompt = f"""Today is {now.strftime("%A, %B %d, %Y")} and the current time is {now.strftime("%H:%M UTC")}.

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a task parser. Extract structured task data from natural language. Return valid JSON only."},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=150,
    )

    data = json.loads(response.choices[0].message.content)

    # Sanitize to guarantee required fields exist
    data.setdefault("title", text[:100])
    data.setdefault("description", None)
    data.setdefault("due_date", None)
    if data.get("priority") not in VALID_PRIORITIES:
        data["priority"] = "Medium"

    return data
