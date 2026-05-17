from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any, AsyncIterator
import uuid

from fastapi import Depends, Request
from sqlalchemy import MetaData, text
from sqlalchemy.orm import Mapped
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session
import structlog

from src.config import settings

logger = structlog.get_logger()

### Database connection config ###
DATABASE_PARAMS: dict[Any, Any] = {}

async_engine: AsyncEngine = create_async_engine(
    url=settings.db.DATABASE_URL_async,
    echo=settings.db.echo,
    **DATABASE_PARAMS,
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    # autobegin=False,
)


async def dispose() -> None:
    await async_engine.dispose()


### Session dependencies ###
async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.
    Separate dependency for background tasks.
    """
    async with async_session_factory() as session:
        yield session


async def get_db_request(request: Request) -> Session:
    """Get database session from request state."""
    session = request.state.db
    return session


SessionDepRequest = Annotated[AsyncSession, Depends(get_db_request)]
SessionDep = Annotated[AsyncSession, Depends(get_db_async)]


### Base SQLAlchemy models ###
class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)


class ModelBase(Base):
    __abstract__ = True
    id: Mapped[uuid.UUID]
