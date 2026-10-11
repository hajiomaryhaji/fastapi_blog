from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from uuid import UUID

from app.application.services.user_service import UserService
from app.core.database import get_db_session
from app.domain.models.user import UserEntity
from app.infrastructure.db.repositories.user_repository_impl import SQLAlchemyUserRepository
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserEntity:
    """Resolve the authenticated user for the current request."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise authentication_error()
        user_id = UUID(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
        raise authentication_error() from exc

    service = UserService(SQLAlchemyUserRepository(session))
    user = await service.get_by_id(user_id)

    if user is None:
        raise authentication_error()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user
