# Sana — Final Testing Checklist

Two kinds of testing here: the automated backend tests (catch
wiring regressions automatically, run in seconds) and this manual
checklist (catches everything that only shows up on a real device
with a real network connection — which is most of what can still go
wrong).

## Automated backend tests

```
cd sana-backend
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

`test_routes_registered.py` and `test_tool_registry.py` exist
specifically because of two real bugs found while building this:
routers defined but never included in `main.py`, and a tool defined
but never imported anywhere. Both would have shipped completely
silently without a test explicitly checking for them. Run this
suite after any future change to `main.py`, `brain.py`, or any
`api/*.py` / tool file — it takes seconds and catches the exact
mistake class that already happened twice.

**Note:** I wrote and syntax-checked these tests, but couldn't
actually execute `pytest` in this environment (no network access
to install `fastapi`/`supabase`/`google-genai`) — run it yourself
before trusting it fully.

---

## Manual end-to-end checklist

### 1. Backend deployment
- [ ] `GET /health` on the live Render URL returns `{"status": "healthy", "assistant": "Sana"}`
- [ ] First request after idle time — measure the actual cold-start delay on the free tier. Decide now if that's acceptable for launch.

### 2. Sign-in
- [ ] Fresh install, no Google account previously used with the app -> account picker shows ALL accounts on the device (tests `setFilterByAuthorizedAccounts(false)`)
- [ ] Sign in -> land on chat screen, not sign-in screen
- [ ] Force-close the app, reopen -> lands directly on chat screen (session persisted), not sign-in again
- [ ] Sign out (if/when a sign-out button is added to the UI — not built yet) -> returns to sign-in screen
- [ ] Test on a **release-signed** build specifically, not just debug — this is the #1 way Google Sign-In silently breaks (different SHA-1 fingerprint)

### 3. Typed chat
- [ ] Send a message -> reply appears, feels like it's actually "Sana" (check the identity/tone, not a generic assistant)
- [ ] Send a second message in the same session -> reply shows awareness of the first message (context is working)
- [ ] Close and reopen the app -> new conversation started (known gap — no history UI yet, confirm this is expected, not broken)
- [ ] Say something personal/durable ("I wake up at 7am") in one session, ask about it in a later session -> confirms long-term memory (not just conversation history) is actually working

### 4. Tool calling / actions — typed
- [ ] Type "set a 5 minute timer" -> Sana's reply acknowledges it BEFORE the timer fires (confirms the function-call round-trip, not just a canned response)
- [ ] Wait for the timer -> notification appears AND it speaks aloud
- [ ] Check Render logs / `GET /actions/result` -> confirms the Android app actually reported success back
- [ ] Try an invalid case: "set a timer for -5 minutes" or "for 2 days" -> should fail gracefully (the backend's validation), not crash

### 5. Voice mode (Gemini Live)
- [ ] Tap the mic button -> orb shows LISTENING, speak -> orb shows THINKING then SPEAKING, hear Sana's actual voice back
- [ ] Say "Hey Sana, are you there" with the phone actively playing her reply out loud -> confirm she does NOT hear/react to her own voice (tests the `VOICE_COMMUNICATION` echo cancellation actually works on your specific device — this varies by manufacturer)
- [ ] Ask for a timer BY VOICE -> confirm it executes identically to the typed version (same executor, same notification, same reporting)
- [ ] Turn off wifi mid-conversation -> confirm it fails visibly (ERROR state) rather than hanging silently
- [ ] Leave voice mode open and idle for a few minutes -> check battery/data usage afterward, decide if this needs a timeout

### 6. Permissions
- [ ] Deny microphone permission at the OS prompt -> try voice mode -> currently fails silently (known gap) — confirm this is acceptable for now or prioritize fixing it
- [ ] On Android 12+ specifically, check whether `SCHEDULE_EXACT_ALARM` actually works without extra user action — this is the single most likely permission to silently misbehave, and it varies by Android version

### 7. Full "AI wife" experience check
- [ ] Read back a few real conversations and honestly assess: does the tone/personality match what you actually want from Sana, or does it still feel generic? (The identity file controls this — `app/core/identity.py` — and hasn't been tuned since the JTech -> Sana rename beyond the name itself.)

---

## What "final testing" does NOT cover yet (be aware, not alarmed)

- Automated Android UI tests (Compose testing / Espresso) — none exist; everything Android-side is manual-only for now
- Load testing (what happens with many simultaneous users) — not relevant yet at your current stage, but worth remembering before wider release
- No settings screen exists yet to test (voice on/off, tone, timezone) — the backend supports it, nothing in the app calls it
