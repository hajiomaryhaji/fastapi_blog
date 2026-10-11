from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.domain.models.user import UserEntity

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

@dataclass
class PostEntity:
    user_id: UUID
    title: str
    content: str
    author: UserEntity | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
