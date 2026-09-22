"""
Sana AI — Conversation Service

Handles persistent conversations and messages.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class ConversationService:
    """Handles Sana conversations and messages."""

    def _get_authenticated_client(
        self,
        access_token: str,
    ) -> Client:
        """Create a Supabase client for the authenticated user."""

        client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key,
        )

        client.postgrest.auth(access_token)

        return client

    async def create_conversation(
        self,
        user_id: str,
        access_token: str,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Create a new conversation."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("conversations")
            .insert(
                {
                    "user_id": user_id,
                    "title": title,
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to create conversation."
            )

        return response.data[0]

    async def get_conversations(
        self,
        user_id: str,
        access_token: str,
    ) -> list[dict[str, Any]]:
        """Get all conversations for the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("conversations")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )

        return response.data or []

    async def save_message(
        self,
        user_id: str,
        access_token: str,
        conversation_id: str,
        role: str,
        content: str,
    ) -> dict[str, Any]:
        """Save a message to a conversation."""

        if role not in {
            "user",
            "assistant",
            "system",
        }:
            raise ValueError("Invalid message role.")

        if not content.strip():
            raise ValueError(
                "Message content cannot be empty."
            )

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("messages")
            .insert(
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "role": role,
                    "content": content.strip(),
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to save message."
            )

        return response.data[0]

    async def get_messages(
        self,
        user_id: str,
        access_token: str,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        """Get messages from a conversation."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .execute()
        )

        return response.data or []


conversation_service = ConversationService()
