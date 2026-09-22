"""
JTech AI — Permissions Service

Handles JTech-level permission preferences for
authenticated users.

Android system permissions remain controlled by Android.
"""

from typing import Any

from supabase import Client, create_client

from app.core.config import settings


class PermissionService:
    """Handles JTech user permission preferences."""

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

    async def get_permissions(
        self,
        user_id: str,
        access_token: str,
    ) -> list[dict[str, Any]]:
        """Get permission preferences for the user."""

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("user_permissions")
            .select("*")
            .eq("user_id", user_id)
            .order("permission")
            .execute()
        )

        return response.data or []

    async def set_permission(
        self,
        user_id: str,
        access_token: str,
        permission: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Enable or disable a JTech permission preference."""

        if not permission.strip():
            raise ValueError(
                "Permission name cannot be empty."
            )

        client = self._get_authenticated_client(
            access_token
        )

        response = (
            client
            .table("user_permissions")
            .upsert(
                {
                    "user_id": user_id,
                    "permission": permission.strip(),
                    "enabled": enabled,
                },
                on_conflict="user_id,permission",
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Failed to update permission."
            )

        return response.data[0]


permission_service = PermissionService()
