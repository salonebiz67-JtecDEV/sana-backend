# Sana — Gemini Live Voice

Real-time, always-listening voice conversation with Sana, using
Gemini's Live API. This is different from (and more advanced than)
a wake-word → speech-to-text → chat → text-to-speech loop: audio
streams continuously in both directions over one WebSocket
connection to your backend, which relays it to/from Gemini Live.

## Why the backend sits in the middle

The Gemini API key must never ship inside the Android app. Your
backend (`app/api/live.py`, `app/live/service.py`) holds the real
Gemini connection; the app only ever talks to *your* backend over
a WebSocket, authenticated with the same Supabase token it already
uses for `/chat`.

```
Android mic  ──PCM 16kHz──▶  your backend  ──Live API──▶  Gemini
Android speaker ◀──PCM 24kHz── your backend ◀──Live API── Gemini
                              │
                              └─ tool calls (create_timer, etc.)
                                 handled with the SAME tool_registry
                                 as text chat — Sana behaves
                                 identically whether typed or spoken
```

## Files

- `LiveVoiceState.kt` — IDLE / LISTENING / THINKING / SPEAKING / ERROR, matching the state diagram from earlier planning
- `LiveVoiceClient.kt` — the whole client: opens the WebSocket, captures mic audio via `AudioRecord`, streams it out, plays incoming audio via `AudioTrack`, and surfaces actions (like a requested timer) through a callback so you can hand them to `ActionDispatcher` from the actions module we built earlier

## Required manifest permission

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

This is a **runtime** permission (Android 6+) — request it before calling `start()`, or it will throw a `SecurityException`.

## Required Gradle dependencies

```kotlin
implementation("com.squareup.okhttp3:okhttp:4.12.0")       // likely already added for ActionReporter
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
```

## Usage

```kotlin
val liveClient = LiveVoiceClient(
    backendWsUrl = "wss://your-app.onrender.com/live/ws",
    accessToken = supabaseAccessToken,
    conversationId = currentConversationId, // optional, ties voice into existing chat history
    onStateChange = { state -> updateOrbUi(state) },
    onAction = { action ->
        // Route through the same dispatcher built for the action system
        lifecycleScope.launch {
            val result = actionDispatcher.dispatch(action)
            actionReporter.report(accessToken, result)
        }
    },
    onError = { message -> showError(message) },
)

liveClient.start()
// ... later, when the user ends the conversation:
liveClient.stop()
```

## Honest gaps and things to verify before relying on this

- **Model name churn**: `app/live/service.py` on the backend hardcodes a specific Gemini live/native-audio model id. These preview model names get renamed/deprecated more often than stable models — check Google AI Studio for the current one before you deploy, not just at first setup.
- **`VOICE_COMMUNICATION` audio source**: used in `LiveVoiceClient` because it applies echo cancellation, which matters a lot here since the phone is simultaneously playing Sana's voice out loud while listening — without it you risk Sana hearing (and reacting to) her own voice. Test on a real device; behavior varies by manufacturer.
- **No local voice-activity detection (VAD) yet.** Right now the mic streams continuously the whole time the session is open; Gemini Live's own server-side VAD decides when your "turn" has ended. If you want a push-to-talk button instead, call `signalEndOfTurn()` when the user releases it.
- **Network interruptions aren't specially handled.** A dropped WebSocket currently just ends the session (`onFailure` → `stop()`). Automatic reconnection isn't built yet — worth adding once this is being used in the real world, not just tested locally.
- **Battery/data cost**: continuous bidirectional audio streaming is meaningfully more expensive (battery, mobile data, and Gemini API cost) than a wake-word-triggered exchange. This mode is best entered deliberately (e.g. tapping a "talk to Sana" button) rather than running in the background all the time.
