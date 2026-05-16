__all__ = ("router",)
import structlog
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import stamina
from redis.exceptions import ConnectionError, TimeoutError
from src.repositories.cache import CacheRepositoryProtocol, get_cache_repository
from src.repositories.crud.db import get_db_request


from .schemas import (
    LivenessResponseSchema,
    ReadinessResponseSchema,
    ServiceStatusSchema,
)

logger = structlog.get_logger()


router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@router.get(
    "/liveness",
    description="Application status",
    response_model=LivenessResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_healthcheck_live_status() -> LivenessResponseSchema:
    """
    Liveness check for the application
    """
    return LivenessResponseSchema()


@router.get(
    "/readiness",
    description="Application status",
    response_model=ReadinessResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_healthcheck_read_status(
    session: Annotated[AsyncSession, Depends(get_db_request)],
    cache: Annotated[CacheRepositoryProtocol, Depends(get_cache_repository)],
) -> ReadinessResponseSchema:
    """
    Readiness check for the application
    """
    #### DB Healthcheck ####
    status = ReadinessResponseSchema()
    try:

        await session.execute(text("SELECT 1"))
        status.service.append(ServiceStatusSchema(service="db", status="healthy"))
    except Exception as e:
        status.service.append(ServiceStatusSchema(service="db", status="not_healthy"))
        status.status = "not_healthy"
        logger.error("Database unhealthy", exc_info=e)

    #### Redis Healthcheck ####
    try:
        async for attempt in stamina.retry_context(
            on=(ConnectionError, TimeoutError),
            attempts=2,
        ):
            with attempt:
                await cache.set("healthcheck", "healthcheck")
                res = await cache.get("healthcheck")
                if res is None or res != "healthcheck":
                    raise ConnectionError("Redis unhealthy")
        status.service.append(ServiceStatusSchema(service="redis", status="healthy"))
    except Exception as e:
        status.service.append(
            ServiceStatusSchema(service="redis", status="not_healthy")
        )
        status.status = "not_healthy"
        logger.error("Redis unhealthy", exc_info=e)

    return status
