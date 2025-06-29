# app/services/categorizer.py
import os
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv


load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALID_CATEGORIES = ["Work", "Personal", "Learning", "Health", "Finance", "Home", "Other"]

def get_task_category(title: str, description: Optional[str] = None) -> str:
    """
    Uses OpenAI GPT to categorize a task based on its title and description.
    """
    prompt_content = f"""
    Categorize the following task into one of the following categories: {', '.join(VALID_CATEGORIES)}.
    Respond with only the category name.

    Task Title: "{title}"
    Task Description: "{description or 'No description'}"

    Category:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert task organizer."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.0,
            max_tokens=10,
        )
        category = response.choices[0].message.content.strip()
        # Ensure the AI returns a valid category
        return category if category in VALID_CATEGORIES else "Other"
    except Exception as e:
        print(f"Error calling OpenAI for categorization: {e}")
        # Fallback to a default category in case of API error
        return "Uncategorized"