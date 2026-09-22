"""
JTech AI — AI Service

Coordinates conversations, long-term memory,
and the JTech AI brain.
"""

from typing import Any

from app.ai.brain import jtech_brain
from app.conversation.service import conversation_service
from app.memory.service import memory_service


class AIService:
    """Coordinates the complete JTech AI request flow."""

    async def process_message(
        self,
        user_id: str,
        access_token: str,
        user_message: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Process a user message using conversation history,
        long-term memory, and the JTech AI brain.
        """

        user_message = user_message.strip()

        if not user_message:
            raise ValueError(
                "Message cannot be empty."
            )

        # --------------------------------------------
        # CREATE OR USE CONVERSATION
        # --------------------------------------------

        if conversation_id is None:
            conversation = (
                await conversation_service.create_conversation(
                    user_id=user_id,
                    access_token=access_token,
                )
            )

            conversation_id = conversation["id"]

        # --------------------------------------------
        # LOAD CONVERSATION HISTORY
        # --------------------------------------------

        previous_messages = (
            await conversation_service.get_messages(
                user_id=user_id,
                access_token=access_token,
                conversation_id=conversation_id,
            )
        )

        # --------------------------------------------
        # LOAD LONG-TERM MEMORY
        # --------------------------------------------

        memory_context = (
            await memory_service.get_memory_context(
                user_id=user_id,
                access_token=access_token,
            )
        )

        # --------------------------------------------
        # SAVE USER MESSAGE
        # --------------------------------------------

        await conversation_service.save_message(
            user_id=user_id,
            access_token=access_token,
            conversation_id=conversation_id,
            role="user",
            content=user_message,
        )

        # --------------------------------------------
        # GENERATE JTECH RESPONSE
        # --------------------------------------------

        response = jtech_brain.generate_response(
            user_message=user_message,
            conversation_messages=previous_messages,
            memory_context=memory_context,
        )

        # --------------------------------------------
        # SAVE JTECH RESPONSE
        # --------------------------------------------

        await conversation_service.save_message(
            user_id=user_id,
            access_token=access_token,
            conversation_id=conversation_id,
            role="assistant",
            content=response,
        )

        return {
            "message": response,
            "conversation_id": conversation_id,
        }


ai_service = AIService()
