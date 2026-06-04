# app/services/breakdown.py
from openai import OpenAI
import json
from typing import Optional

client = OpenAI()

def generate_subtasks(title: str, description: Optional[str] = None) -> list[str]:
    prompt = f'Break down this task into 4 to 6 specific, actionable subtasks.\nTask: "{title}"'
    if description:
        prompt += f'\nContext: {description}'
    prompt += '\nReturn a JSON object with a single key "subtasks" containing an array of concise subtask title strings.'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=300,
    )

    data = json.loads(response.choices[0].message.content)
    return [str(t) for t in data.get("subtasks", [])]
