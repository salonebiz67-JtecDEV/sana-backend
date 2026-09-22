"""
Sana AI — Brain

Handles communication between the Sana backend
and the Gemini API.
"""

from google import genai

from app.ai.context import build_ai_context
from app.core.config import settings
from app.ai.prompts import SYSTEM_PROMPT


class SanaBrain:
    """Core AI engine for Sana."""

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def generate_response(
        self,
        user_message: str,
        conversation_messages: list[dict] | None = None,
        memory_context: str = "",
    ) -> str:
        """
        Send a user message and available context
        to Gemini.
        """

        ai_context = build_ai_context(
            conversation_messages=conversation_messages,
            memory_context=memory_context,
        )

        if ai_context:
            prompt = (
                f"{ai_context}\n\n"
                "CURRENT USER MESSAGE:\n"
                f"{user_message}"
            )
        else:
            prompt = user_message

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
            },
        )

        if not response.text:
            return "I wasn't able to generate a response."

        return response.text


sana_brain = SanaBrain()
