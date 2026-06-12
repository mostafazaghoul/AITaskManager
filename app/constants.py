"""Domain constants shared across the application.

Centralizes the valid priority and category values so that schemas,
services, and routes never drift out of sync with each other.
"""
from typing import Literal, get_args

# Priority levels a task can have. ``Priority`` is used for request
# validation; ``VALID_PRIORITIES`` is the same set as a runtime tuple.
Priority = Literal["High", "Medium", "Low"]
VALID_PRIORITIES: tuple[str, ...] = get_args(Priority)
DEFAULT_PRIORITY: str = "Medium"

# Categories the AI categorizer is allowed to choose from.
VALID_CATEGORIES: tuple[str, ...] = (
    "Work",
    "Personal",
    "Learning",
    "Health",
    "Finance",
    "Home",
    "Other",
)

# Category assigned when the AI picks something unexpected.
FALLBACK_CATEGORY: str = "Other"

# Category a task holds before (or if) categorization runs.
DEFAULT_CATEGORY: str = "Uncategorized"
