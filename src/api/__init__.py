__all__ = ("api_router",)
from fastapi import APIRouter

from src.config import settings

from .api_v1 import api_router as api_v1_router
from .healthcheck import router as healthcheck_router

api_router = APIRouter(prefix=settings.api.prefix)

api_router.include_router(api_v1_router)
api_router.include_router(healthcheck_router)
