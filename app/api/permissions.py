"""
Sana AI — Permissions API

Endpoints for managing Sana-level permission preferences.

Android system permissions remain controlled by Android.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.permissions.service import permission_service


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


class SetPermissionRequest(BaseModel):
    permission: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    enabled: bool


@router.get("")
async def get_permissions(
    current_user: dict = Depends(get_current_user),
):
    """Get Sana permission preferences."""

    try:
        permissions = (
            await permission_service.get_permissions(
                user_id=current_user["id"],
                access_token=current_user["access_token"],
            )
        )

        return {
            "permissions": permissions,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve permissions.",
        ) from exc


@router.put("")
async def set_permission(
    request: SetPermissionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Enable or disable a Sana permission preference."""

    try:
        permission = (
            await permission_service.set_permission(
                user_id=current_user["id"],
                access_token=current_user["access_token"],
                permission=request.permission,
                enabled=request.enabled,
            )
        )

        return {
            "permission": permission,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to update permission.",
        ) from exc
