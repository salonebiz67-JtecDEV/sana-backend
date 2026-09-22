"""
Sana AI — Timer Tool

Defines the timer action that Sana can request.

The backend does not directly control Android.
It returns a structured action for the Android client
to execute safely.
"""

from typing import Any

from app.ai.tools import SanaTool, tool_registry


async def create_timer(
    duration_seconds: int,
    label: str = "Timer",
) -> dict[str, Any]:
    """
    Create a timer action for the Android client.
    """

    if duration_seconds <= 0:
        raise ValueError(
            "Timer duration must be greater than zero."
        )

    if duration_seconds > 86400:
        raise ValueError(
            "Timer duration cannot exceed 24 hours."
        )

    label = label.strip()

    if not label:
        label = "Timer"

    return {
        "status": "action_required",
        "action": {
            "type": "create_timer",
            "duration_seconds": duration_seconds,
            "label": label,
        },
    }


timer_tool = SanaTool(
    name="create_timer",
    description=(
        "Create a timer on the user's Android device. "
        "Use this when the user asks Sana to set or "
        "start a countdown timer."
    ),
    parameters={
        "type": "object",
        "properties": {
            "duration_seconds": {
                "type": "integer",
                "description": (
                    "Timer duration in seconds."
                ),
            },
            "label": {
                "type": "string",
                "description": (
                    "Optional label for the timer."
                ),
            },
        },
        "required": [
            "duration_seconds",
        ],
    },
    handler=create_timer,
)


tool_registry.register(timer_tool)
