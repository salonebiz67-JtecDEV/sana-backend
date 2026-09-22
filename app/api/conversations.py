"""
Sana AI — Conversation API

Endpoints for persistent conversations and messages.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.conversation.service import conversation_service


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


class CreateConversationRequest(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=200,
    )


class SaveMessageRequest(BaseModel):
    role: str = Field(
        ...,
        pattern="^(user|assistant|system)$",
    )

    content: str = Field(
        ...,
        min_length=1,
    )


@router.post("")
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a conversation for the authenticated user."""

    try:
        conversation = await conversation_service.create_conversation(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            title=request.title,
        )

        return {
            "conversation": conversation,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to create conversation.",
        ) from exc


@router.get("")
async def get_conversations(
    current_user: dict = Depends(get_current_user),
):
    """Get the authenticated user's conversations."""

    try:
        conversations = await conversation_service.get_conversations(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
        )

        return {
            "conversations": conversations,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversations.",
        ) from exc


@router.post("/{conversation_id}/messages")
async def save_message(
    conversation_id: str,
    request: SaveMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Save a message to a conversation."""

    try:
        message = await conversation_service.save_message(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            conversation_id=conversation_id,
            role=request.role,
            content=request.content,
        )

        return {
            "message": message,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to save message.",
        ) from exc


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get messages from a conversation."""

    try:
        messages = await conversation_service.get_messages(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            conversation_id=conversation_id,
        )

        return {
            "messages": messages,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve messages.",
        ) from exc
