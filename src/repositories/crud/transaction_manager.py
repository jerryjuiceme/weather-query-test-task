from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Self

from fastapi import Depends
import sqlalchemy as sa

from .db import get_db_request


# from sqlalchemy.ext.asyncio import AsyncSession
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TransactionService:
    """
    Represents a service for working with transactions.
    """

    def __init__(self, session: "AsyncSession") -> None:
        self.session = session

    @asynccontextmanager
    async def begin(self: Self, immediate: bool = True) -> AsyncIterator[None]:
        """
        Start a transaction.
        """
        async with self.session.begin():
            if immediate:
                await self.session.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))
            yield


async def get_transaction_service(
    session: "AsyncSession" = Depends(get_db_request),
) -> TransactionService:
    return TransactionService(session)
