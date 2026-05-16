__all__ = ["WeatherRepository"]

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from .db import get_db_request

from .weather import WeatherRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

###############################
## REPOSITORIES DEPENDENCIES ##
###############################


async def get_weather_repository(
    session: Annotated["AsyncSession", Depends(get_db_request)],
) -> WeatherRepository:
    return WeatherRepository(session=session)


# NoteRepositoryDep = Annotated[NoteRepository, Depends(get_note_repository)]
