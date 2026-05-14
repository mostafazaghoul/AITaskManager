# app/services/planner.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from .. import schemas

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_daily_plan(tasks: List[schemas.Task]) -> str:
    """
    Generates a smart, prioritized daily plan using OpenAI GPT.
    """
    if not tasks:
        return "No tasks for today! Time to relax or add some new ones."

    task_list_str = "\n".join(
        f"- [{task.priority}] {task.title} "
        f"(Due: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'No due date'}, "
        f"Category: {task.category})"
        for task in tasks
    )

    prompt_content = f"""
    You are a productivity expert. Given the following tasks (each tagged with a priority level),
    create a smart, prioritized daily schedule. Schedule High priority tasks during peak morning hours.
    Group related tasks by context (e.g. 'Deep Work', 'Errands', 'Admin'). Suggest a realistic
    timeline and be encouraging.

    Tasks:
    {task_list_str}

    Your suggested plan:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a world-class productivity coach."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI for planning: {e}")
        return "Could not generate a plan due to an error. Please check your tasks and try again."