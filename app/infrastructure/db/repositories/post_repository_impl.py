from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.domain.interfaces.post_repository import IPostRepository
from app.domain.models.post import PostEntity
from app.domain.models.user import UserEntity
from app.infrastructure.db.models.post_orm import PostORM


class SQLAlchemyPostRepository(IPostRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, post_id: UUID) -> Optional[PostEntity]:
        stmt = (
            select(PostORM)
            .options(selectinload(PostORM.author))
            .where(PostORM.id == post_id)
        )
        result = await self.session.execute(stmt)
        post_orm = result.scalars().first()

        if not post_orm:
            return None

        return self._to_entity(post_orm)

    async def get_by_title(self, title: str) -> Optional[PostEntity]:
        stmt = (
            select(PostORM)
            .options(selectinload(PostORM.author))
            .where(PostORM.title == title)
        )
        result = await self.session.execute(stmt)
        post_orm = result.scalars().first()

        if not post_orm:
            return None

        return self._to_entity(post_orm)

    async def list_all(self) -> list[PostEntity]:
        stmt = (
            select(PostORM)
            .options(selectinload(PostORM.author))
            .order_by(PostORM.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(post_orm) for post_orm in result.scalars().all()]

    async def create(self, post: PostEntity) -> PostEntity:
        post_orm = PostORM(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        self.session.add(post_orm)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(post_orm)

        created_post = await self.get_by_id(post_orm.id)
        if created_post is None:
            raise RuntimeError("The post was created but could not be loaded.")
        return created_post

    async def update(
        self,
        post_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Optional[PostEntity]:
        stmt = (
            select(PostORM)
            .options(selectinload(PostORM.author))
            .where(PostORM.id == post_id, PostORM.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        post_orm = result.scalars().first()

        # Treat a missing post and a post owned by another user identically.
        if post_orm is None:
            return None

        if title is not None:
            post_orm.title = title
        if content is not None:
            post_orm.content = content

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(post_orm)

        return await self.get_by_id(post_id)

    async def delete(self, post_id: UUID, user_id: UUID) -> bool:
        stmt = (
            select(PostORM)
            .options(selectinload(PostORM.author))
            .where(PostORM.id == post_id, PostORM.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        post_orm = result.scalars().first()

        if post_orm is None:
            return False

        await self.session.delete(post_orm)
        await self.session.commit()

        return True



    @staticmethod
    def _to_entity(post_orm: PostORM) -> PostEntity:
        return PostEntity(
            id=post_orm.id,
            user_id=post_orm.user_id,
            title=post_orm.title,
            content=post_orm.content,
            created_at=post_orm.created_at,
            updated_at=post_orm.updated_at,
            author=UserEntity(
                id=post_orm.author.id,
                name=post_orm.author.name,
                email=post_orm.author.email,
                password_hash=post_orm.author.password_hash,
                is_active=post_orm.author.is_active,
                created_at=post_orm.author.created_at,
                updated_at=post_orm.author.updated_at,
            ),
        )
