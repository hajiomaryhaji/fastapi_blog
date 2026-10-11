from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from app.domain.models.user import UserEntity

class IUserRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[UserEntity]: ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]: ...

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity: ...

    @abstractmethod
    async def update(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
    ) -> Optional[UserEntity]: ...

    @abstractmethod
    async def deactivate(self, user_id: UUID) -> bool: ...
