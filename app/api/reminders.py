"""
Sana AI — Reminders API

Endpoints for managing authenticated user reminders.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.reminders.service import reminder_service


router = APIRouter(
    prefix="/reminders",
    tags=["Reminders"],
)


class CreateReminderRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    message: str | None = None

    remind_at: str = Field(
        ...,
        min_length=1,
    )

    repeat_rule: str | None = None


class UpdateReminderRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    message: str | None = None

    remind_at: str | None = None

    status: str | None = Field(
        default=None,
        pattern="^(scheduled|triggered|cancelled)$",
    )

    repeat_rule: str | None = None


@router.post("")
async def create_reminder(
    request: CreateReminderRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a reminder for the authenticated user."""

    try:
        reminder = await reminder_service.create_reminder(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            title=request.title,
            message=request.message,
            remind_at=request.remind_at,
            repeat_rule=request.repeat_rule,
        )

        return {
            "reminder": reminder,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to create reminder.",
        ) from exc


@router.get("")
async def get_reminders(
    current_user: dict = Depends(get_current_user),
):
    """Get reminders belonging to the authenticated user."""

    try:
        reminders = await reminder_service.get_reminders(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
        )

        return {
            "reminders": reminders,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve reminders.",
        ) from exc


@router.patch("/{reminder_id}")
async def update_reminder(
    reminder_id: str,
    request: UpdateReminderRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update a reminder belonging to the authenticated user."""

    updates = request.model_dump(
        exclude_none=True
    )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No reminder changes were provided.",
        )

    try:
        reminder = await reminder_service.update_reminder(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            reminder_id=reminder_id,
            updates=updates,
        )

        return {
            "reminder": reminder,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to update reminder.",
        ) from exc


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a reminder belonging to the authenticated user."""

    try:
        await reminder_service.delete_reminder(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            reminder_id=reminder_id,
        )

        return {
            "status": "deleted",
            "reminder_id": reminder_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete reminder.",
        ) from exc
