from uuid import UUID
from typing import Optional

from app.domain.interfaces.post_repository import IPostRepository
from app.domain.models.post import PostEntity
from app.application.dtos.post_dto import PostCreateRequest, PostUpdateRequest

class PostService:
    def __init__(self, repository: IPostRepository) -> None:
        self.repository = repository

    async def list_posts(self) -> list[PostEntity]:
        return await self.repository.list_all()

    async def get_by_id(self, post_id: UUID) -> Optional[PostEntity]:
        return await self.repository.get_by_id(post_id)

    async def create_post(self, request: PostCreateRequest, user_id: UUID) -> PostEntity:
        title = str(request.title).strip()
        content = str(request.content).strip()

        post = PostEntity(
            user_id=user_id,
            title=title,
            content=content
        )
        return await self.repository.create(post)

    async def update_post(
        self,
        post_id: UUID,
        request: PostUpdateRequest,
        user_id: UUID,
    ) -> Optional[PostEntity]:
        return await self.repository.update(
            post_id=post_id,
            user_id=user_id,
            title=request.title,
            content=request.content,
        )

    async def delete_post(self, post_id: UUID, user_id: UUID) -> bool:
        return await self.repository.delete(post_id, user_id)
