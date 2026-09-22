"""
Sana AI — User Settings API

Endpoints for persistent user preferences.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.settings.service import settings_service


router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)


class UpdateSettingsRequest(BaseModel):
    assistant_name: str | None = None
    voice_enabled: bool | None = None
    voice_name: str | None = None
    response_style: str | None = None
    notifications_enabled: bool | None = None
    memory_enabled: bool | None = None
    proactive_assistance_enabled: bool | None = None


@router.get("")
async def get_settings(
    current_user: dict = Depends(get_current_user),
):
    """Get settings for the authenticated user."""

    try:
        user_settings = (
            await settings_service.get_settings(
                user_id=current_user["id"],
                access_token=current_user["access_token"],
            )
        )

        return {
            "settings": user_settings,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve settings.",
        ) from exc


@router.patch("")
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update settings for the authenticated user."""

    updates: dict[str, Any] = request.model_dump(
        exclude_none=True
    )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No settings were provided.",
        )

    try:
        user_settings = (
            await settings_service.update_settings(
                user_id=current_user["id"],
                access_token=current_user["access_token"],
                updates=updates,
            )
        )

        return {
            "settings": user_settings,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to update settings.",
        ) from exc
