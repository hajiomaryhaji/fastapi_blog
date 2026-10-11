from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator, model_validator

from uuid import UUID
from datetime import datetime

class UserPublicResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserPrivateResponse(UserPublicResponse):
    email: EmailStr

class UserCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=120)
    password: SecretStr = Field(min_length=8, max_length=128)


class UserUpdateRequest(BaseModel):
    """Fields the authenticated user may change."""

    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    password: SecretStr | None = Field(default=None, min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_a_change(self) -> "UserUpdateRequest":
        if self.name is None and self.email is None and self.password is None:
            raise ValueError("At least one user field must be provided")
        return self
