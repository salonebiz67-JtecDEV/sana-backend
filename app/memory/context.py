"""
Sana AI — Memory Context

Builds relevant long-term memory context for Sana.
"""

from typing import Any


def build_memory_context(
    memories: list[dict[str, Any]],
    max_memories: int = 10,
) -> str:
    """
    Convert stored memories into a compact context
    that can be provided to Sana.
    """

    if not memories:
        return ""

    selected_memories = memories[:max_memories]

    context_lines: list[str] = []

    for memory in selected_memories:
        category = memory.get(
            "category",
            "general",
        )

        content = memory.get(
            "content",
            "",
        )

        importance = memory.get(
            "importance",
            5,
        )

        if not content:
            continue

        context_lines.append(
            f"- [{category}] "
            f"{content} "
            f"(importance: {importance}/10)"
        )

    if not context_lines:
        return ""

    return "\n".join(context_lines)
