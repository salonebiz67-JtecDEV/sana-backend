"""
Sana AI — Live Voice Session

Manages one real-time voice session between an Android client and
the Gemini Live API. The backend sits in the middle so the Gemini
API key never has to live on the device:

    Android (mic audio) --WebSocket--> Sana backend --Live API--> Gemini
    Android (speaker)   <--WebSocket-- Sana backend <--Live API-- Gemini

This reuses the same tool registry as the text-based brain (brain.py),
so anything voice asks Sana to do (e.g. "set a 20 minute timer") goes
through the exact same create_timer -> SanaAction -> Android executor
pipeline as typed chat does.

NOTE ON MODEL NAME: Gemini's live/native-audio model names are
frequently renamed as new preview versions ship. Verify the current
model id in Google AI Studio / the Gemini API docs before deploying —
"gemini-2.5-flash-native-audio-preview-12-2025" below may already be
superseded by the time you read this.
"""

from typing import Any

from google import genai
from google.genai import types

from app.ai.context import build_ai_context
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import tool_registry
from app.conversation.service import conversation_service
from app.core.config import settings
from app.memory.service import memory_service

# Registers the timer tool (and any future tools) into tool_registry
# as an import side effect — same reason brain.py imports this.
from app.ai import tools_timer  # noqa: F401


LIVE_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

# Live API audio contract (fixed by Gemini, not configurable):
INPUT_SAMPLE_RATE = 16000   # what we must send Gemini
OUTPUT_SAMPLE_RATE = 24000  # what Gemini sends back


class LiveVoiceSession:
    """
    One active Gemini Live session for one authenticated user.
    Create a fresh instance per WebSocket connection.
    """

    def __init__(
        self,
        user_id: str,
        access_token: str,
        conversation_id: str | None = None,
    ) -> None:
        self.user_id = user_id
        self.access_token = access_token
        self.conversation_id = conversation_id
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.pending_action: dict[str, Any] | None = None

    async def build_session_config(self) -> types.LiveConnectConfig:
        """
        Build the Live session config, injecting Sana's system prompt
        plus the user's long-term memory and recent conversation —
        so voice mode "knows" the user exactly like text chat does.
        """

        memory_context = await memory_service.get_memory_context(
            user_id=self.user_id,
            access_token=self.access_token,
        )

        previous_messages: list[dict[str, Any]] = []
        if self.conversation_id:
            previous_messages = await conversation_service.get_messages(
                user_id=self.user_id,
                access_token=self.access_token,
                conversation_id=self.conversation_id,
            )

        extra_context = build_ai_context(
            conversation_messages=previous_messages,
            memory_context=memory_context,
        )

        system_instruction = SYSTEM_PROMPT
        if extra_context:
            system_instruction = f"{SYSTEM_PROMPT}\n\n{extra_context}"

        tools = tool_registry.get_gemini_tools()

        return types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=system_instruction,
            tools=(
                [{"function_declarations": tools}]
                if tools
                else None
            ),
        )

    async def send_audio_chunk(self, session, chunk: bytes) -> None:
        """Forward one raw PCM audio chunk from the device to Gemini."""

        await session.send_realtime_input(
            audio=types.Blob(
                data=chunk,
                mime_type=f"audio/pcm;rate={INPUT_SAMPLE_RATE}",
            )
        )

    async def handle_server_message(self, session, message) -> bytes | None:
        """
        Process one message from Gemini. Returns raw PCM audio bytes
        to play back to the user, if this message contained audio.
        Tool calls are executed here transparently — the caller
        (the WebSocket route) doesn't need to know they happened,
        except to relay self.pending_action to Android afterward.
        """

        # Tool call requested mid-conversation
        if getattr(message, "tool_call", None):
            for function_call in message.tool_call.function_calls:
                await self._handle_tool_call(session, function_call)
            return None

        # Audio/text output from the model
        server_content = getattr(message, "server_content", None)
        if server_content and server_content.model_turn:
            for part in server_content.model_turn.parts:
                if part.inline_data:
                    return part.inline_data.data

        return None

    async def _handle_tool_call(self, session, function_call) -> None:
        """Execute a tool Gemini requested, same as the text brain does."""

        tool = tool_registry.get(function_call.name)

        if tool is None:
            result: dict[str, Any] = {
                "status": "error",
                "error": f"Unknown tool '{function_call.name}'.",
            }
        else:
            args = dict(function_call.args or {})
            try:
                result = await tool.handler(**args)
            except Exception as exc:
                result = {"status": "error", "error": str(exc)}

        if result.get("status") == "action_required":
            action_data = dict(result.get("action", {}))
            action_type = action_data.pop("type", None)
            if action_type:
                self.pending_action = {
                    "type": action_type,
                    "parameters": action_data,
                }

        await session.send_tool_response(
            function_responses=[
                types.FunctionResponse(
                    id=function_call.id,
                    name=function_call.name,
                    response=result,
                )
            ]
        )

    def take_pending_action(self) -> dict[str, Any] | None:
        """
        Return and clear the most recent action requested during this
        session, so the WebSocket route can forward it to Android
        as a structured message (not audio).
        """

        action = self.pending_action
        self.pending_action = None
        return action
              
