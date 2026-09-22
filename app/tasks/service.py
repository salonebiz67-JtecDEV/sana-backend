"""
JTech AI — Tasks Service

Handles persistent tasks for authenticated users.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class TaskService:
    """Handles JTech user tasks."""

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

    async def create_task(
        self,
        user_id: str,
        access_token: str,
        title: str,
        description: str | None = None,
        priority: str = "normal",
        due_at: str | None = None,
    ) -> dict[str, Any]:
        """Create a task for the authenticated user."""

        if not title.strip():
            raise ValueError(
                "Task title cannot be empty."
            )

        if priority not in {
            "low",
            "normal",
            "high",
            "urgent",
        }:
            raise ValueError(
                "Invalid task priority."
            )

        client = self._get_authenticated_client(
            access_token
        )

        task_data = {
            "user_id": user_id,
            "title": title.strip(),
            "description": description,
            "priority": priority,
        }

        if due_at is not None:
            task_data["due_at"] = due_at

        response = (
            client
            .table("tasks")
            .insert(task_data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to create task."
            )

        return response.data[0]

    async def get_tasks(
        self,
        user_id: str,
        access_token: str,
    ) -> list[dict[str, Any]]:
        """Get all tasks belonging to the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    async def update_task(
        self,
        user_id: str,
        access_token: str,
        task_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a task belonging to the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("tasks")
            .update(updates)
            .eq("id", task_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Task not found or could not be updated."
            )

        return response.data[0]

    async def delete_task(
        self,
        user_id: str,
        access_token: str,
        task_id: str,
    ) -> None:
        """Delete a task belonging to the authenticated user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("tasks")
            .delete()
            .eq("id", task_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Task not found or could not be deleted."
            )


task_service = TaskService()
