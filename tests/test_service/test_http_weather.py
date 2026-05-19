import uuid

from dirty_equals import IsUUID

from src.schemas import WeatherRead
from src.services.http.weather import WeatherHttpService


class TestWeatherHttpService:
    async def test_with_api_mocked(self, http_weather_service: WeatherHttpService):
        # Act
        result = await http_weather_service.fetch_weather(
            city="Jonkoping",
            units="metric",
            user_id=uuid.uuid4(),
        )
        # Assert
        assert isinstance(result, WeatherRead)
        assert not result.is_from_cache

    async def test_from_cache(self, http_weather_service: WeatherHttpService):
        # Act
        result = await http_weather_service.fetch_weather(
            city="Berlin",
            units="metric",
            user_id=uuid.uuid4(),
        )
        result = await http_weather_service.fetch_weather(
            city="Berlin",
            units="metric",
            user_id=uuid.uuid4(),
        )

        # Assert
        assert result.id == IsUUID()
        assert result.is_from_cache

    async def test_not_from_cache(self, http_weather_service: WeatherHttpService):
        # Act
        result = await http_weather_service.fetch_weather(
            city="Berlin",
            units="metric",
            user_id=uuid.uuid4(),
        )
        result = await http_weather_service.fetch_weather(
            city="New York",
            units="metric",
            user_id=uuid.uuid4(),
        )

        # Assert
        assert isinstance(result, WeatherRead)
        assert not result.is_from_cache
