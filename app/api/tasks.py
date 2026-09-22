"""
Sana AI — Tasks API

Endpoints for managing authenticated user tasks.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.tasks.service import task_service


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


class CreateTaskRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    description: str | None = None

    priority: str = Field(
        default="normal",
        pattern="^(low|normal|high|urgent)$",
    )

    due_at: str | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    description: str | None = None

    status: str | None = Field(
        default=None,
        pattern="^(pending|in_progress|completed|cancelled)$",
    )

    priority: str | None = Field(
        default=None,
        pattern="^(low|normal|high|urgent)$",
    )

    due_at: str | None = None


@router.post("")
async def create_task(
    request: CreateTaskRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a task for the authenticated user."""

    try:
        task = await task_service.create_task(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            title=request.title,
            description=request.description,
            priority=request.priority,
            due_at=request.due_at,
        )

        return {
            "task": task,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to create task.",
        ) from exc


@router.get("")
async def get_tasks(
    current_user: dict = Depends(get_current_user),
):
    """Get tasks belonging to the authenticated user."""

    try:
        tasks = await task_service.get_tasks(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
        )

        return {
            "tasks": tasks,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve tasks.",
        ) from exc


@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update a task belonging to the authenticated user."""

    updates = request.model_dump(
        exclude_none=True
    )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No task changes were provided.",
        )

    if (
        updates.get("status") == "completed"
        and "completed_at" not in updates
    ):
        from datetime import datetime, timezone

        updates["completed_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

    try:
        task = await task_service.update_task(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            task_id=task_id,
            updates=updates,
        )

        return {
            "task": task,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to update task.",
        ) from exc


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a task belonging to the authenticated user."""

    try:
        await task_service.delete_task(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            task_id=task_id,
        )

        return {
            "status": "deleted",
            "task_id": task_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete task.",
        ) from exc
