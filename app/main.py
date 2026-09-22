"""
Sana AI Backend
"""

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.ai.service import ai_service
from app.api.conversations import (
    router as conversations_router,
)
from app.api.memory import router as memory_router
from app.api.settings import router as settings_router
from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.core.identity import (
    AI_FULL_NAME,
    AI_NAME,
    DEVELOPER_NAME,
)


app = FastAPI(
    title=AI_FULL_NAME,
    version=settings.app_version,
    description="Backend for Sana AI.",
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
    )

    conversation_id: str | None = None


class ChatResponse(BaseModel):
    assistant: str
    message: str
    user_id: str
    conversation_id: str


app.include_router(memory_router)

app.include_router(conversations_router)

app.include_router(settings_router)


@app.get("/")
async def root():
    return {
        "name": AI_NAME,
        "full_name": AI_FULL_NAME,
        "developer": DEVELOPER_NAME,
        "version": settings.app_version,
        "status": "online",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "assistant": AI_NAME,
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a message to Sana as an authenticated user.

    The AI service handles conversation history,
    long-term memory, Gemini processing, and
    message persistence.
    """

    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        result = await ai_service.process_message(
            user_id=current_user["id"],
            access_token=current_user["access_token"],
            user_message=user_message,
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            assistant=AI_NAME,
            message=result["message"],
            user_id=current_user["id"],
            conversation_id=result["conversation_id"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Sana was unable to process the request.",
        ) from exc
      
