from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.application.dtos.user_dto import UserCreateRequest, UserPublicResponse, UserPrivateResponse, UserUpdateRequest
from app.application.services.user_service import UserAlreadyExistsError, UserService
from app.core.database import get_db_session
from app.domain.models.user import UserEntity
from app.infrastructure.db.repositories.user_repository_impl import SQLAlchemyUserRepository

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(SQLAlchemyUserRepository(session))


@router.get("", response_model=list[UserPublicResponse])
async def get_users(
    service: UserService = Depends(get_user_service),
) -> list[UserPublicResponse]:
    return [UserPublicResponse.model_validate(user) for user in await service.list_users()]


@router.get("/me", response_model=UserPrivateResponse)
async def get_current_user_profile(
    current_user: UserEntity = Depends(get_current_user),
) -> UserPrivateResponse:
    return UserPrivateResponse.model_validate(current_user)


@router.post("", response_model=UserPrivateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service),
) -> UserPrivateResponse:
    try:
        user = await service.create_user(request)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        # The unique database constraint is the final protection against a race.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc

    return UserPrivateResponse.model_validate(user)


@router.patch("/me", response_model=UserPrivateResponse)
async def update_current_user(
    request: UserUpdateRequest,
    current_user: UserEntity = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPrivateResponse:
    try:
        user = await service.update_user(current_user.id, request)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserPrivateResponse.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: UserEntity = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> Response:
    deleted = await service.delete_user(current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{user_id}", response_model=Optional[UserPublicResponse])
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    user = await service.get_by_id(user_id)

    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
