__all__ = ["WeatherService"]

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

# from .note_on_base import NoteService
from src.repositories.crud import WeatherRepository
from src.repositories.crud.db import get_db_async
from .weather import WeatherService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


###########################
## SERVICES DEPENDENCIES ##
###########################


def get_weather_service(
    session: Annotated["AsyncSession", Depends(get_db_async)],
) -> WeatherService:
    repository = WeatherRepository(session=session)
    return WeatherService(repository=repository)


WeatherServiceDep = Annotated[WeatherService, Depends(get_weather_service)]
