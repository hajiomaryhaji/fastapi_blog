from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timezone

def _utc_now():
    return datetime.now(timezone.utc)

@dataclass
class UserEntity:
    name: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
