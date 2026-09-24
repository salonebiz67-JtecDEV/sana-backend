"""
Sana AI — Test Configuration

Provides fake environment variables so app.core.config.Settings
loads successfully during tests, without needing real Gemini or
Supabase credentials. These tests never actually call Gemini or
Supabase — they check the app's own wiring (routers, tool
registration), not third-party services.
"""

import os

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
