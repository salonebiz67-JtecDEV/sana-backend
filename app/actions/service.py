"""
Sana AI — Actions Service

Handles logging the outcome of actions that the backend
requested and the Android client attempted to execute.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class ActionService:
    """Handles Sana action result logging."""

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

    async def log_action_result(
        self,
        user_id: str,
        access_token: str,
        action_type: str,
        success: bool,
        message: str = "",
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log the result of an action executed by the Android client."""

        if not action_type.strip():
            raise ValueError(
                "action_type cannot be empty."
            )

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("action_logs")
            .insert(
                {
                    "user_id": user_id,
                    "action_type": action_type.strip(),
                    "success": success,
                    "message": message,
                    "data": data or {},
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to log action result."
            )

        return response.data[0]

    async def get_action_logs(
        self,
        user_id: str,
        access_token: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get recent action logs for the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("action_logs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data or []


action_service = ActionService()
