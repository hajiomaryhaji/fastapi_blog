from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.token_dto import JWT
from app.application.services.user_service import UserService
from app.core.database import get_db_session
from app.core.security import create_access_token, verify_password
from app.infrastructure.db.repositories.user_repository_impl import SQLAlchemyUserRepository


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=JWT)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> JWT:
    """Authenticate with an email/password form and issue a bearer token."""
    service = UserService(SQLAlchemyUserRepository(session))
    user = await service.get_by_email(credentials.username.strip().lower())

    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return JWT(
        access_token=create_access_token(str(user.id)),
        token_type="bearer",
    )
