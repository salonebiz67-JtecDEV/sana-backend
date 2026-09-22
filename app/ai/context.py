"""
Sana AI — AI Context

Builds the complete context that can be provided
to the Sana AI brain.
"""

from typing import Any


def build_conversation_context(
    messages: list[dict[str, Any]],
) -> str:
    """
    Convert stored conversation messages into
    readable conversation context.
    """

    if not messages:
        return ""

    context_lines: list[str] = []

    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")

        if not content:
            continue

        if role == "user":
            speaker = "User"
        elif role == "assistant":
            speaker = "Sana"
        elif role == "system":
            speaker = "System"
        else:
            continue

        context_lines.append(
            f"{speaker}: {content}"
        )

    return "\n".join(context_lines)


def build_ai_context(
    conversation_messages: list[dict[str, Any]] | None = None,
    memory_context: str = "",
) -> str:
    """
    Build the complete context for Sana.

    Combines current conversation history with
    relevant long-term memories.
    """

    conversation_context = build_conversation_context(
        conversation_messages or []
    )

    context_sections: list[str] = []

    if memory_context.strip():
        context_sections.append(
            "RELEVANT LONG-TERM MEMORY:\n"
            f"{memory_context.strip()}"
        )

    if conversation_context.strip():
        context_sections.append(
            "CURRENT CONVERSATION:\n"
            f"{conversation_context.strip()}"
        )

    return "\n\n".join(context_sections)
