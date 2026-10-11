from __future__ import annotations

from sqlalchemy import Boolean, UUID as SQLAlchemyUUID, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.core.database import Base
if TYPE_CHECKING:
    from app.infrastructure.db.models.post_orm import PostORM


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True, index=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )

    posts: Mapped[list[PostORM]] = relationship("PostORM", back_populates="author")
