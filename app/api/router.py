from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import posts
from app.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(posts.router)
api_router.include_router(users.router)
