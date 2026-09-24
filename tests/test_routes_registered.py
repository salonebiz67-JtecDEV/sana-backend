"""
Sana AI — Router Registration Test

This test exists specifically because of a real bug found during
development: three fully-written API routers (permissions,
reminders, tasks) were never registered in app/main.py, making
their endpoints completely unreachable despite the code existing
and looking correct.

If a new api/*.py file is ever added and someone forgets the
matching app.include_router() call in main.py, this test fails
loudly instead of the bug silently shipping.
"""

from app.main import app

EXPECTED_PREFIXES = [
    "/health",
    "/chat",
    "/memory",
    "/actions",
    "/conversations",
    "/settings",
    "/permissions",
    "/reminders",
    "/tasks",
]


def _registered_paths() -> list[str]:
    return [route.path for route in app.routes]


def test_every_expected_prefix_is_registered():
    paths = _registered_paths()

    for prefix in EXPECTED_PREFIXES:
        matching = [p for p in paths if p == prefix or p.startswith(prefix + "/")]
        assert matching, (
            f"No route found for expected prefix '{prefix}'. "
            f"Did you forget app.include_router(...) in app/main.py? "
            f"All registered paths: {paths}"
        )


def test_live_voice_websocket_is_registered():
    paths = _registered_paths()
    assert "/live/ws" in paths, (
        "The /live/ws WebSocket route is missing from the app. "
        f"All registered paths: {paths}"
    )


def test_no_duplicate_routes():
    """
    Catches the opposite mistake: the same router accidentally
    included twice (e.g. copy-pasted an include_router line).
    """
    paths = _registered_paths()
    seen = set()
    duplicates = set()

    for path in paths:
        if path in seen:
            duplicates.add(path)
        seen.add(path)

    assert not duplicates, f"Duplicate routes registered: {duplicates}"
