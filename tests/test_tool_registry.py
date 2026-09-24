"""
Sana AI — Tool Registration Test

Exists specifically because of a real bug found during development:
app/ai/tools_timer.py correctly defined and registered the timer
tool as an import side effect, but nothing in the project actually
imported that module — so tool_registry never contained
"create_timer" at runtime, silently. Gemini would have had no idea
the tool existed.

Importing app.ai.brain (which imports tools_timer) is what actually
triggers registration — this test imports it the same way the real
app does, rather than importing tools_timer directly, so it catches
the exact class of mistake that happened before.
"""

import app.ai.brain  # noqa: F401  (import side effect registers tools)
from app.ai.tools import tool_registry

EXPECTED_TOOLS = [
    "create_timer",
]


def test_every_expected_tool_is_registered():
    registered_names = [tool.name for tool in tool_registry.list_tools()]

    for name in EXPECTED_TOOLS:
        assert tool_registry.get(name) is not None, (
            f"Tool '{name}' is not registered in tool_registry. "
            f"Was its module imported anywhere (e.g. in app/ai/brain.py)? "
            f"Currently registered: {registered_names}"
        )


def test_gemini_tool_declarations_are_well_formed():
    """
    Every registered tool must produce a valid Gemini function
    declaration (name + description at minimum), or Gemini will
    reject the whole request at call time instead of failing here.
    """

    declarations = tool_registry.get_gemini_tools()

    assert len(declarations) >= len(EXPECTED_TOOLS)

    for declaration in declarations:
        assert "name" in declaration and declaration["name"], (
            f"Tool declaration missing a name: {declaration}"
        )
        assert "description" in declaration and declaration["description"], (
            f"Tool '{declaration.get('name')}' is missing a description, "
            "which Gemini needs to decide when to call it."
        )
      
