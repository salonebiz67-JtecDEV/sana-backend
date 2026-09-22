"""
Sana AI — Memory API

Endpoints for managing the authenticated user's memories.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.memory.service import memory_service


router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


class SaveMemoryRequest(BaseModel):
    category: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    importance: int = Field(default=5, ge=1, le=10)


@router.post("")
async def save_memory(
    request: SaveMemoryRequest,
    current_user: dict = Depends(get_current_user),
):
    """Save a memory for the authenticated user."""

    try:
        memory = await memory_service.save_memory(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            category=request.category,
            content=request.content,
            importance=request.importance,
        )

        return {
            "status": "saved",
            "memory": memory,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to save memory.",
        ) from exc


@router.get("")
async def get_memories(
    current_user: dict = Depends(get_current_user),
):
    """Get memories for the authenticated user."""

    try:
        memories = await memory_service.get_memories(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
        )

        return {
            "memories": memories,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve memories.",
        ) from exc
