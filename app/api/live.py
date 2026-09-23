"""
Sana AI — Live Voice API

WebSocket endpoint for real-time voice conversations with Sana.
The Android client streams raw 16kHz PCM audio in, and receives raw
24kHz PCM audio back, plus occasional JSON text frames when an
action (e.g. create_timer) needs to be executed on-device.

Auth: since WebSocket handshakes don't support FastAPI's normal
HTTPBearer/Depends flow, the client must send the Supabase access
token as an "Authorization: Bearer <token>" header on the WebSocket
handshake request itself (OkHttp on Android supports this directly).
"""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.dependencies import verify_access_token
from app.live.service import LiveVoiceSession


router = APIRouter(
    tags=["Live Voice"],
)


@router.websocket("/live/ws")
async def live_voice_ws(websocket: WebSocket):
    """
    Real-time voice session.

    Query params:
        conversation_id (optional) - ties this voice session's
            context into an existing text conversation's history.
    """

    auth_header = websocket.headers.get("authorization", "")

    if not auth_header.lower().startswith("bearer "):
        await websocket.close(code=4401)
        return

    access_token = auth_header[len("bearer "):].strip()

    try:
        current_user = await verify_access_token(access_token)
    except Exception:
        await websocket.close(code=4401)
        return

    await websocket.accept()

    conversation_id = websocket.query_params.get("conversation_id")

    live_session = LiveVoiceSession(
        user_id=current_user["id"],
        access_token=current_user["access_token"],
        conversation_id=conversation_id,
    )

    try:
        config = await live_session.build_session_config()
    except Exception as exc:
        await websocket.send_text(
            json.dumps({"type": "error", "message": str(exc)})
        )
        await websocket.close(code=1011)
        return

    try:
        async with live_session.client.aio.live.connect(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            config=config,
        ) as gemini_session:

            async def relay_android_to_gemini():
                """Read audio (or control messages) from Android, forward to Gemini."""
                while True:
                    message = await websocket.receive()

                    if message["type"] == "websocket.disconnect":
                        return

                    if (audio_bytes := message.get("bytes")) is not None:
                        await live_session.send_audio_chunk(
                            gemini_session, audio_bytes
                        )
                        continue

                    if (text := message.get("text")) is not None:
                        # Reserved for control messages, e.g. {"type": "end_turn"}
                        try:
                            payload = json.loads(text)
                        except json.JSONDecodeError:
                            continue

                        if payload.get("type") == "end_turn":
                            await gemini_session.send_realtime_input(
                                audio_stream_end=True
                            )

            async def relay_gemini_to_android():
                """Read Gemini's responses, forward audio/actions to Android."""
                async for message in gemini_session.receive():
                    audio_chunk = await live_session.handle_server_message(
                        gemini_session, message
                    )

                    if audio_chunk is not None:
                        await websocket.send_bytes(audio_chunk)

                    action = live_session.take_pending_action()
                    if action is not None:
                        await websocket.send_text(
                            json.dumps({"type": "action", "action": action})
                        )

            android_task = asyncio.create_task(relay_android_to_gemini())
            gemini_task = asyncio.create_task(relay_gemini_to_android())

            done, pending = await asyncio.wait(
                [android_task, gemini_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

    except WebSocketDisconnect:
        pass

    except Exception as exc:
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "message": str(exc)})
            )
        except Exception:
            pass

    finally:
        try:
            await websocket.close()
        except Exception:
            pass
                              
