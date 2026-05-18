import uuid
from datetime import datetime, timezone

# import pytest
from dirty_equals import IsUUID


from .repository import TempTestRepository
from .schemas import TempTestCreate, TempTestRead

from src.repositories.crud import WeatherRepository
from src.schemas import WeatherRead
from src.schemas.pagination import FilterSchema, PaginationSchema
from src.schemas.weather import WeatherOutputMessage


class TestDBRepository:
    async def test_get_all(self, test_repository: TempTestRepository):
        # Arrange
        result = await test_repository.get_all()

        # Assert
        assert result
        assert len(result) == 5
        assert isinstance(result[0], TempTestRead)

    async def test_get_one_or_none(
        self, test_data_params, test_repository: TempTestRepository
    ):
        # Arrange
        id_ = test_data_params[0]["id"]
        # Act
        result = await test_repository.get_one_or_none(id_)
        # Assert
        assert isinstance(result, TempTestRead)
        assert result.id == uuid.UUID(id_)

    async def test_create(self, test_repository: TempTestRepository):
        # Arrange
        create_object = TempTestCreate(
            str_column="test_str",
            int_column=1,
            float_column=1.0,
            bool_column=True,
        )
        # Act
        result = await test_repository.create(create_object)

        # Assert
        assert isinstance(result, TempTestRead)
        assert result.str_column == "test_str"
        assert result.id == IsUUID()

    async def test_delete(self, test_data_params, test_repository: TempTestRepository):
        # Arrange
        id_ = test_data_params[0]["id"]
        await test_repository.delete(id_)

        # Assert
        result = await test_repository.get_one_or_none(id_)
        assert result is None


class TestWeatherRepository:

    async def test_get_history_paginated_returns_all(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_paginated(
            pagination=PaginationSchema(limit=10, offset=0),
            filter_schema=FilterSchema(),
            sort_by=None,
            order_by=None,
        )

        # Assert
        assert result.total_count == 4
        assert len(result.objects) == 4
        assert isinstance(result.objects[0], WeatherRead)

    async def test_get_history_paginated_respects_limit_and_offset(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_paginated(
            pagination=PaginationSchema(limit=2, offset=1),
            filter_schema=FilterSchema(),
            sort_by="id",
            order_by="asc",
        )

        # Assert
        assert result.total_count == 4
        assert result.filtered_count == 2

    async def test_get_history_paginated_filters_by_city_substring(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_paginated(
            pagination=PaginationSchema(limit=10, offset=0),
            filter_schema=FilterSchema(city_substring="er"),
            sort_by=None,
            order_by=None,
        )

        # Assert
        print(result)
        assert result.total_count == 1
        assert all("er" in obj.city_name.lower() for obj in result.objects)

    async def test_get_history_paginated_filters_by_date_from(
        self, test_weather_repository: WeatherRepository
    ):
        # Arrange
        future = datetime(2099, 1, 1, tzinfo=timezone.utc)

        # Act
        result = await test_weather_repository.get_history_paginated(
            pagination=PaginationSchema(limit=10, offset=0),
            filter_schema=FilterSchema(date_from=future),
            sort_by=None,
            order_by=None,
        )

        # Assert
        assert result.total_count == 0
        assert result.objects == []

    async def test_get_history_filtered_returns_all(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_filtered(
            filter_schema=FilterSchema(),
        )

        # Assert
        assert len(result) == 4
        assert isinstance(result[0], WeatherOutputMessage)

    async def test_get_history_filtered_by_city_substring(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_filtered(
            filter_schema=FilterSchema(city_substring="Los"),
        )

        # Assert
        assert len(result) == 1
        assert result[0].city_name == "Los Angeles"

    async def test_get_history_filtered_default_sort_order(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_filtered(
            filter_schema=FilterSchema(),
            sort_by="created_at",
            order_by="desc",
        )

        # Assert
        assert len(result) == 4
        assert result[0].created_at >= result[-1].created_at

    async def test_get_history_filtered_no_results(
        self, test_weather_repository: WeatherRepository
    ):
        # Act
        result = await test_weather_repository.get_history_filtered(
            filter_schema=FilterSchema(city_substring="Blalala"),
        )

        # Assert
        assert result == []
