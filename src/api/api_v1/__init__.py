from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from src.config import settings

from .weather import router as weather_router
from .history import router as history_router
from .auth import router as auth_router
from .users import router as users_router

http_bearer = HTTPBearer(auto_error=False)

api_router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[
        Depends(http_bearer),
    ],
)

api_router.include_router(weather_router)
api_router.include_router(history_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
