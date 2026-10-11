from __future__ import annotations

from sqlalchemy import String, UUID as SQLAlchemyUUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.core.database import Base
if TYPE_CHECKING:
    from app.infrastructure.db.models.user_orm import UserORM


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PostORM(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )

    author: Mapped[UserORM] = relationship("UserORM", back_populates="posts")
