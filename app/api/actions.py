"""
Sana AI — Actions API

Endpoint for the Android client to report back the result
of executing an action that Sana requested (e.g. create_timer).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.actions.service import action_service
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/actions",
    tags=["Actions"],
)


class ActionResultRequest(BaseModel):
    action_type: str = Field(
        ...,
        min_length=1,
    )

    success: bool

    message: str = ""

    data: dict[str, Any] = Field(
        default_factory=dict,
    )


@router.post("/result")
async def report_action_result(
    request: ActionResultRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Report whether an action requested by Sana was
    successfully executed on the Android device.
    """

    try:
        log = await action_service.log_action_result(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            action_type=request.action_type,
            success=request.success,
            message=request.message,
            data=request.data,
        )

        return {
            "log": log,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to log action result.",
        ) from exc


@router.get("/result")
async def get_action_logs(
    current_user: dict = Depends(get_current_user),
):
    """Get recent action logs for the authenticated user."""

    try:
        logs = await action_service.get_action_logs(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
        )

        return {
            "logs": logs,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve action logs.",
        ) from exc
