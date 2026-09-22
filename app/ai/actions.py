"""
Sana AI — Action Contracts

Defines the standard structure for actions that the
backend can request from the Android application.
"""

from typing import Any

from pydantic import BaseModel, Field


class SanaAction(BaseModel):
    """
    An action that the Android client may execute.
    """

    type: str = Field(
        ...,
        min_length=1,
    )

    requires_confirmation: bool = False

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )


class SanaActionResult(BaseModel):
    """
    Result returned by the Android client after
    attempting to execute an action.
    """

    action_type: str = Field(
        ...,
        min_length=1,
    )

    success: bool

    message: str

    data: dict[str, Any] = Field(
        default_factory=dict
    )
