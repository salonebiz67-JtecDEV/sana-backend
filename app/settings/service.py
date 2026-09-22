"""
JTech AI — User Settings Service

Handles persistent settings for authenticated users.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class SettingsService:
    """Handles JTech user settings."""

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

    async def get_settings(
        self,
        user_id: str,
        access_token: str,
    ) -> dict[str, Any]:
        """Get settings for the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("user_settings")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if response.data:
            return response.data

        return {
            "user_id": user_id,
            "assistant_name": "JTech",
            "voice_enabled": True,
            "voice_name": None,
            "response_style": "natural",
            "notifications_enabled": True,
            "memory_enabled": True,
            "proactive_assistance_enabled": True,
        }

    async def update_settings(
        self,
        user_id: str,
        access_token: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update settings for the user."""

        client = self._get_authenticated_client(
            access_token
        )

        existing = (
            client
            .table("user_settings")
            .select("user_id")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if existing.data:
            response = (
                client
                .table("user_settings")
                .update(updates)
                .eq("user_id", user_id)
                .execute()
            )
        else:
            response = (
                client
                .table("user_settings")
                .insert(
                    {
                        "user_id": user_id,
                        **updates,
                    }
                )
                .execute()
            )

        if not response.data:
            raise RuntimeError(
                "Failed to update user settings."
            )

        return response.data[0]


settings_service = SettingsService()
