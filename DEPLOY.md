# Sana — Deploying the Backend to Render

## Steps

1. Push `sana-backend` to GitHub (`main` branch) if you haven't already — `render.yaml` assumes that branch name.
2. In Render: **New +** -> **Blueprint** -> connect your `sana-backend` repo. Render reads `render.yaml` automatically and creates the web service for you.
3. Render will ask you to fill in the environment variables marked `sync: false` — these are deliberately **not** committed to the repo:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (the **service_role** key — this backend needs elevated access to run each request in the user's own auth context; never put this key in the Android app)
4. Click **Apply**. First deploy takes a few minutes.
5. Once live, test it:
   ```
   curl https://your-service-name.onrender.com/health
   ```
   Should return `{"status": "healthy", "assistant": "Sana"}`.
6. Update your Android app's backend URL (used by `ActionReporter`, `LiveVoiceClient`, and wherever you call `/chat`) to this Render URL — `https://` for normal requests, `wss://` for the `/live/ws` WebSocket.

## Honest things to know before relying on this in the real world

- **Free tier sleeps.** Render's free web services spin down after ~15 minutes of no traffic, and the next request pays a cold-start penalty (often 30–60+ seconds) while it spins back up. For typed chat that's a bad first impression; for `/live/ws` (a real-time voice session) it's worse — the connection could time out before the service even wakes up. If you want voice mode to feel responsive in practice, you'll likely need a paid plan that doesn't sleep, or a lightweight external "ping every N minutes" keep-alive — but that keep-alive also burns your free-tier hours, so it's a real tradeoff, not a free fix.
- **WebSockets work on Render's web services** (no special config needed beyond what's in `render.yaml` already) — but they still respect the same sleep/cold-start behavior above.
- **This blueprint deploys the Python backend only.** It has nothing to do with deploying the Android app — that goes to the Play Store (or gets installed directly as an APK) through an entirely separate process.
- **Region matters for latency**, especially for voice — pick the Render region closest to where you (or your actual users) are, not just the default.

## What I fixed while preparing this deployment

While wiring this up I found three API routers that existed in the codebase (`permissions`, `reminders`, `tasks`) but were never registered in `app/main.py` — meaning those endpoints were completely unreachable even though the code for them was fully written. I've added the missing imports and `include_router` calls; see the updated `app/main.py`.
