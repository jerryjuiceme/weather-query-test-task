from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import Depends

from src.repositories.crud.models import User
from src.repositories.crud.db import get_db_request


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated["AsyncSession", Depends(get_db_request)],
):
    yield User.get_db(session=session)
