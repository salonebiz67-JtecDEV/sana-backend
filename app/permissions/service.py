"""
Sana AI — Reminders Service

Handles persistent reminders for authenticated users.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class ReminderService:
    """Handles Sana user reminders."""

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

    async def create_reminder(
        self,
        user_id: str,
        access_token: str,
        title: str,
        remind_at: str,
        message: str | None = None,
        repeat_rule: str | None = None,
    ) -> dict[str, Any]:
        """Create a reminder for the authenticated user."""

        if not title.strip():
            raise ValueError(
                "Reminder title cannot be empty."
            )

        if not remind_at.strip():
            raise ValueError(
                "Reminder time cannot be empty."
            )

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("reminders")
            .insert(
                {
                    "user_id": user_id,
                    "title": title.strip(),
                    "message": message,
                    "remind_at": remind_at,
                    "repeat_rule": repeat_rule,
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to create reminder."
            )

        return response.data[0]

    async def get_reminders(
        self,
        user_id: str,
        access_token: str,
    ) -> list[dict[str, Any]]:
        """Get reminders belonging to the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("reminders")
            .select("*")
            .eq("user_id", user_id)
            .order("remind_at", desc=False)
            .execute()
        )

        return response.data or []

    async def update_reminder(
        self,
        user_id: str,
        access_token: str,
        reminder_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a reminder belonging to the user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("reminders")
            .update(updates)
            .eq("id", reminder_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Reminder not found or could not be updated."
            )

        return response.data[0]

    async def delete_reminder(
        self,
        user_id: str,
        access_token: str,
        reminder_id: str,
    ) -> None:
        """Delete a reminder belonging to the user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("reminders")
            .delete()
            .eq("id", reminder_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Reminder not found or could not be deleted."
            )


reminder_service = ReminderService()
