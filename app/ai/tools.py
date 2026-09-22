"""
Sana AI — Tool System

Defines the foundation for Sana tools.

Gemini may request a tool, but the backend controls
which tools exist and how they are executed.
"""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


ToolHandler = Callable[..., Awaitable[dict[str, Any]]]


@dataclass
class SanaTool:
    """Represents a tool available to Sana."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler


class ToolRegistry:
    """Registry for all Sana tools."""

    def __init__(self) -> None:
        self._tools: dict[str, SanaTool] = {}

    def register(
        self,
        tool: SanaTool,
    ) -> None:
        """Register a Sana tool."""

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> SanaTool | None:
        """Get a registered tool by name."""

        return self._tools.get(name)

    def list_tools(self) -> list[SanaTool]:
        """Return all registered tools."""

        return list(self._tools.values())

    def get_gemini_tools(self) -> list[dict[str, Any]]:
        """
        Convert registered tools into a Gemini-compatible
        function declaration structure.
        """

        declarations: list[dict[str, Any]] = []

        for tool in self._tools.values():
            declarations.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            )

        return declarations


tool_registry = ToolRegistry()
