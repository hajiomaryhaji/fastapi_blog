from typing import Optional
from uuid import UUID

from app.application.dtos.user_dto import UserCreateRequest, UserUpdateRequest
from app.core.security import hash_password
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.models.user import UserEntity


class UserAlreadyExistsError(Exception):
    """Raised when a user cannot be created because the email is taken."""


class UserService:
    def __init__(self, repository: IUserRepository) -> None:
        self.repository = repository

    async def list_users(self) -> list[UserEntity]:
        return await self.repository.list_all()

    async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        return await self.repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        return await self.repository.get_by_email(email)

    async def create_user(self, request: UserCreateRequest) -> UserEntity:
        name = request.name.strip()
        email = str(request.email).strip().lower()
        if await self.get_by_email(email):
            raise UserAlreadyExistsError(
                "A user with this email already exists.")

        user = UserEntity(
            name=name,
            email=email,
            password_hash=hash_password(request.password.get_secret_value()),
        )
        return await self.repository.create(user)

    async def update_user(
        self,
        user_id: UUID,
        request: UserUpdateRequest,
    ) -> Optional[UserEntity]:
        name = request.name.strip() if request.name is not None else None
        email = str(request.email).strip().lower() if request.email is not None else None
        password_hash = (
            hash_password(request.password.get_secret_value())
            if request.password is not None
            else None
        )

        if email is not None:
            existing_user = await self.get_by_email(email)
            if existing_user is not None and existing_user.id != user_id:
                raise UserAlreadyExistsError(
                    "A user with this email already exists."
                )

        return await self.repository.update(
            user_id=user_id,
            name=name,
            email=email,
            password_hash=password_hash,
        )

    async def delete_user(self, user_id: UUID) -> bool:
        """Deactivate a user while preserving posts and audit history."""
        return await self.repository.deactivate(user_id)
