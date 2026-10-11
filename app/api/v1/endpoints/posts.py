from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional
from uuid import UUID

from app.core.database import get_db_session
from app.api.dependencies.auth import get_current_user
from app.application.dtos.post_dto import PostCreateRequest, PostResponse, PostUpdateRequest
from app.application.services.post_service import PostService
from app.domain.models.user import UserEntity
from app.infrastructure.db.repositories.post_repository_impl import SQLAlchemyPostRepository

router = APIRouter(prefix="/posts", tags=["Posts"])

def get_post_service(
        session: AsyncSession = Depends(get_db_session)
) -> PostService:
    return PostService(SQLAlchemyPostRepository(session))


@router.get("/", response_model=list[PostResponse])
async def get_posts(
    service: PostService = Depends(get_post_service)
) -> list[PostResponse]:
    return [PostResponse.model_validate(post) for post in await service.list_posts()]


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: PostCreateRequest,
    current_user: UserEntity = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
) -> PostResponse:
    post = await service.create_post(request, user_id=current_user.id)
    return PostResponse.model_validate(post)


@router.get("/{post_id}", response_model=Optional[PostResponse])
async def get_post(
    post_id: UUID,
    service: PostService = Depends(get_post_service)
):
    post = await service.get_by_id(post_id)

    if post:
        return post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    request: PostUpdateRequest,
    current_user: UserEntity = Depends(get_current_user),
    service: PostService = Depends(get_post_service),
) -> PostResponse:
    post = await service.update_post(post_id, request, user_id=current_user.id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return PostResponse.model_validate(post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: UserEntity = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    deleted = await service.delete_post(post_id, user_id=current_user.id)

    if deleted is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"detail": "Deleted"}
    )
