"""
Sana AI — Memory Models

Defines the structure of information that Sana can
store as long-term memory.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """A long-term memory belonging to a user."""

    user_id: str

    category: str = Field(
        ...,
        description="Memory category such as preference, project, or personal.",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="The information Sana should remember.",
    )

    importance: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Importance from 1 to 10.",
    )

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
