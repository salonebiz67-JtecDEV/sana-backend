"""
Sana AI — AI Service

Coordinates conversations, long-term memory,
and the Sana AI brain.
"""

from typing import Any

from app.ai.brain import sana_brain
from app.conversation.service import conversation_service
from app.memory.service import memory_service


class AIService:
    """Coordinates the complete Sana AI request flow."""

    async def process_message(
        self,
        user_id: str,
        access_token: str,
        user_message: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Process a user message using conversation history,
        long-term memory, and the Sana AI brain.
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
        # GENERATE SANA RESPONSE (may include a tool/action)
        # --------------------------------------------

        result = await sana_brain.generate_response(
            user_message=user_message,
            conversation_messages=previous_messages,
            memory_context=memory_context,
        )

        # --------------------------------------------
        # SAVE SANA RESPONSE
        # --------------------------------------------

        await conversation_service.save_message(
            user_id=user_id,
            access_token=access_token,
            conversation_id=conversation_id,
            role="assistant",
            content=result["text"],
        )

        return {
            "message": result["text"],
            "conversation_id": conversation_id,
            "action": result["action"],
        }


ai_service = AIService()
