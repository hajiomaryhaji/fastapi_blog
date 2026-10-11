from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.models.post import PostEntity

class IPostRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[PostEntity]: ...

    @abstractmethod
    async def get_by_id(self, post_id: UUID) -> Optional[PostEntity]: ...

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[PostEntity]: ...

    @abstractmethod
    async def create(self, post: PostEntity) -> PostEntity: ...

    @abstractmethod
    async def update(
        self,
        post_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Optional[PostEntity]: ...

    @abstractmethod
    async def delete(self, post_id: UUID, user_id: UUID) -> bool: ...
