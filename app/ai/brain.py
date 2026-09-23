"""
Sana AI — Brain

Handles communication between the Sana backend
and the Gemini API, including tool/function calling.
"""

from typing import Any

from google import genai

from app.ai.actions import SanaAction
from app.ai.context import build_ai_context
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import tool_registry
from app.core.config import settings

# Importing this registers the timer tool into tool_registry
# as a side effect. Any new tool module must be imported here
# (or somewhere else guaranteed to run at startup) or it will
# never actually be available to Gemini.
from app.ai import tools_timer  # noqa: F401


class SanaBrain:
    """Core AI engine for Sana."""

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    async def generate_response(
        self,
        user_message: str,
        conversation_messages: list[dict] | None = None,
        memory_context: str = "",
    ) -> dict[str, Any]:
        """
        Send a user message and available context to Gemini.

        Returns a dict:
            {
                "text": str,                - Sana's reply to show/speak to the user
                "action": SanaAction | None - an action for Android to execute, if any
            }
        """

        ai_context = build_ai_context(
            conversation_messages=conversation_messages,
            memory_context=memory_context,
        )

        if ai_context:
            prompt = (
                f"{ai_context}\n\n"
                "CURRENT USER MESSAGE:\n"
                f"{user_message}"
            )
        else:
            prompt = user_message

        tools = tool_registry.get_gemini_tools()

        config: dict[str, Any] = {
            "system_instruction": SYSTEM_PROMPT,
        }

        if tools:
            config["tools"] = [
                {"function_declarations": tools}
            ]

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        function_call = self._extract_function_call(response)

        # No tool requested -> just return the plain text reply
        if function_call is None:
            return {
                "text": response.text or (
                    "I wasn't able to generate a response."
                ),
                "action": None,
            }

        return await self._handle_function_call(
            prompt=prompt,
            function_call=function_call,
        )

    async def _handle_function_call(
        self,
        prompt: str,
        function_call: Any,
    ) -> dict[str, Any]:
        """
        Execute the tool Gemini requested, then send the result
        back to Gemini so it can produce a natural-language reply
        to speak/show to the user.
        """

        tool = tool_registry.get(function_call.name)

        if tool is None:
            return {
                "text": (
                    "I tried to do something I don't actually "
                    "know how to do yet."
                ),
                "action": None,
            }

        args = dict(function_call.args or {})

        try:
            result = await tool.handler(**args)
        except Exception as exc:
            result = {
                "status": "error",
                "error": str(exc),
            }

        action = self._build_action(result)

        follow_up = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                },
                {
                    "role": "model",
                    "parts": [
                        {
                            "function_call": {
                                "name": function_call.name,
                                "args": args,
                            }
                        }
                    ],
                },
                {
                    "role": "user",
                    "parts": [
                        {
                            "function_response": {
                                "name": function_call.name,
                                "response": result,
                            }
                        }
                    ],
                },
            ],
            config={
                "system_instruction": SYSTEM_PROMPT,
            },
        )

        text = follow_up.text or "Done."

        return {
            "text": text,
            "action": action,
        }

    def _build_action(
        self,
        result: dict[str, Any],
    ) -> SanaAction | None:
        """
        Convert a tool handler's result into a SanaAction for the
        Android client to execute, if the result requests one.
        """

        if result.get("status") != "action_required":
            return None

        action_data = dict(result.get("action", {}))
        action_type = action_data.pop("type", None)

        if not action_type:
            return None

        return SanaAction(
            type=action_type,
            parameters=action_data,
        )

    def _extract_function_call(
        self,
        response: Any,
    ) -> Any | None:
        """
        Pull the first function call out of a Gemini response,
        if the model requested one instead of replying with text.
        """

        try:
            candidate = response.candidates[0]
            parts = candidate.content.parts or []
        except (AttributeError, IndexError, TypeError):
            return None

        for part in parts:
            function_call = getattr(part, "function_call", None)
            if function_call is not None:
                return function_call

        return None


sana_brain = SanaBrain()
        
