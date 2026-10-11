from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from typing import Optional
from uuid import UUID

from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.db.models.user_orm import UserORM
from app.domain.models.user import UserEntity


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(stmt)
        user_orm = result.scalars().first()

        if not user_orm:
            return None

        return UserEntity(
            id=user_orm.id,
            name=user_orm.name,
            email=user_orm.email,
            password_hash=user_orm.password_hash,
            is_active=user_orm.is_active,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at
        )

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self.session.execute(stmt)
        user_orm = result.scalars().first()

        if not user_orm:
            return None

        return UserEntity(
            id=user_orm.id,
            name=user_orm.name,
            email=user_orm.email,
            password_hash=user_orm.password_hash,
            is_active=user_orm.is_active,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at
        )

    async def list_all(self) -> list[UserEntity]:
        result = await self.session.execute(select(UserORM).order_by(UserORM.updated_at.desc()))
        return [self._to_entity(user_orm) for user_orm in result.scalars().all()]

    async def create(self, user: UserEntity) -> UserEntity:
        user_orm = UserORM(
            id=user.id,
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(user_orm)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(user_orm)

        return UserEntity(
            id=user_orm.id,
            name=user_orm.name,
            email=user_orm.email,
            password_hash=user_orm.password_hash,
            is_active=user_orm.is_active,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at
        )

    async def update(
        self,
        user_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
    ) -> Optional[UserEntity]:
        user_orm = await self._get_orm_by_id(user_id)
        if user_orm is None or not user_orm.is_active:
            return None

        if name is not None:
            user_orm.name = name
        if email is not None:
            user_orm.email = email
        if password_hash is not None:
            user_orm.password_hash = password_hash

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(user_orm)
        return self._to_entity(user_orm)

    async def deactivate(self, user_id: UUID) -> bool:
        user_orm = await self._get_orm_by_id(user_id)
        if user_orm is None or not user_orm.is_active:
            return False

        user_orm.is_active = False
        await self.session.commit()
        return True

    async def _get_orm_by_id(self, user_id: UUID) -> Optional[UserORM]:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    def _to_entity(user_orm: UserORM) -> UserEntity:
        return UserEntity(
            id=user_orm.id,
            name=user_orm.name,
            email=user_orm.email,
            password_hash=user_orm.password_hash,
            is_active=user_orm.is_active,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at,
        )
