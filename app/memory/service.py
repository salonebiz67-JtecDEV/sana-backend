"""
JTech AI — Memory Service

Handles long-term memory operations using Supabase
with authenticated user context.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class MemoryService:
    """Handles JTech long-term memory."""

    def _get_authenticated_client(
        self,
        access_token: str,
    ) -> Client:
        """
        Create a Supabase client and attach the user's
        access token to database requests.
        """

        client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key,
        )

        client.postgrest.auth(access_token)

        return client

    async def save_memory(
        self,
        user_id: str,
        access_token: str,
        category: str,
        content: str,
        importance: int = 5,
    ) -> dict[str, Any]:
        """Save a memory for the authenticated user."""

        if not content.strip():
            raise ValueError("Memory content cannot be empty.")

        if not 1 <= importance <= 10:
            raise ValueError(
                "Memory importance must be between 1 and 10."
            )

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("memories")
            .insert(
                {
                    "user_id": user_id,
                    "category": category,
                    "content": content.strip(),
                    "importance": importance,
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to save memory.")

        return response.data[0]

    async def get_memories(
        self,
        user_id: str,
        access_token: str,
    ) -> list[dict[str, Any]]:
        """Retrieve memories for the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("memories")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    async def get_memory_context(
        self,
        user_id: str,
        access_token: str,
        max_memories: int = 10,
    ) -> str:
        """Build relevant memory context for JTech."""

        from app.memory.context import build_memory_context

        memories = await self.get_memories(
            user_id=user_id,
            access_token=access_token,
        )

        memories.sort(
            key=lambda memory: (
                memory.get("importance", 5),
                memory.get("created_at", ""),
            ),
            reverse=True,
        )

        return build_memory_context(
            memories=memories,
            max_memories=max_memories,
        )


memory_service = MemoryService()
