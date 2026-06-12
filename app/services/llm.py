"""Shared OpenAI client and configuration for all AI services.

The client is created lazily on first use so the application can start
(and all non-AI features keep working) even when no API key is set.
"""
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# The single model used across every AI feature.
OPENAI_MODEL: str = "gpt-4o-mini"

_client: Optional[OpenAI] = None


class AIServiceError(Exception):
    """Raised when an AI request fails or the AI service is unavailable."""


def get_client() -> OpenAI:
    """Return the shared OpenAI client, creating it on first call.

    Returns:
        A configured ``OpenAI`` client instance.

    Raises:
        AIServiceError: If ``OPENAI_API_KEY`` is not set in the environment.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIServiceError(
                "OPENAI_API_KEY is not configured. AI features are unavailable."
            )
        _client = OpenAI(api_key=api_key)
    return _client
