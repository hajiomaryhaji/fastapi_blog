from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from uuid import UUID
from datetime import datetime
from typing import Optional

from app.application.dtos.user_dto import UserPublicResponse

class PostResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    author: UserPublicResponse

    model_config = ConfigDict(from_attributes=True)

class PostCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    content: str = Field(min_length=20, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

class PostUpdateRequest(BaseModel):
    """Fields that may be changed by a PATCH request."""

    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    content: Optional[str] = Field(default=None, min_length=20, max_length=1000)

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_a_change(self) -> "PostUpdateRequest":
        if self.title is None and self.content is None:
            raise ValueError("At least one of title or content must be provided")
        return self
