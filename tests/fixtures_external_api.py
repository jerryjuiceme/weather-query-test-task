import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from tests.async_mock import AsyncMock
from src.repositories.http import HttpRepository
from src.schemas.weather import WeatherData

### Polyfactory Fixtures ###


@register_fixture(name="weather_http_fetch_fct")
class WeatherHttpFetchFactory(ModelFactory[WeatherData]): ...


### MockNoteRepository ###
@pytest.fixture(scope="function")
def mock_weather_http_repository(
    weather_http_fetch_fct: WeatherHttpFetchFactory,
) -> HttpRepository:
    note_repository = HttpRepository()
    note_repository.get_weather_by_city = AsyncMock(
        return_value=weather_http_fetch_fct.build()
    )
    note_repository.ping = AsyncMock(return_value=weather_http_fetch_fct.build())
    return note_repository
