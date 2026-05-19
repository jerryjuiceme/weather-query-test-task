import uuid

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from src.repositories.cache import CacheRepositoryProtocol
from src.services.cache.weather import WeatherCacheService
from src.services.http.weather import WeatherHttpService
from tests.async_mock import AsyncMock
from src.schemas import WeatherRead, PaginationResultSchema
from src.repositories.crud import WeatherRepository
from src.services.db import WeatherService
from src.repositories.http import HttpRepository

### Polyfactory Fixtures ###


@register_fixture(name="weather_read_fct")
class WeatherReadFactory(ModelFactory[WeatherRead]):
    user_id: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000000")
    is_from_cache: bool = False


### Mock Weather Repository ###


@pytest.fixture(scope="function")
def mock_weather_repository(
    weather_read_fct: WeatherReadFactory,
):
    weather_repository = WeatherRepository(session=AsyncMock(return_value=None))
    weather_repository.create = AsyncMock(return_value=weather_read_fct.build())
    weather_repository.get_history_paginated = AsyncMock(
        return_value=PaginationResultSchema(
            objects=[
                weather_read_fct.build(),
                weather_read_fct.build(),
                weather_read_fct.build(),
            ],
            total_count=3,
            filtered_count=3,
        )
    )
    weather_repository.get_history_filtered = AsyncMock(
        return_value=[
            weather_read_fct.build(),
            weather_read_fct.build(),
            weather_read_fct.build(),
        ],
    )

    return weather_repository


### Weather Service ###
@pytest.fixture(scope="function")
def weather_service(
    mock_weather_repository: WeatherRepository,
) -> WeatherService:
    return WeatherService(repository=mock_weather_repository)


@pytest.fixture(scope="function")
def http_weather_service(
    weather_service: WeatherService,
    mock_weather_http_repository: HttpRepository,
    cache_in_memory: CacheRepositoryProtocol,
) -> WeatherHttpService:
    return WeatherHttpService(
        http_repository=mock_weather_http_repository,
        cache_service=WeatherCacheService(cache_repository=cache_in_memory),
        crud=weather_service,
    )


### IDs Params Fixtures ###
# @dataclass
# class IDTypesParams:
#     input_id: uuid.UUID | str
#     expected: Any


# @pytest.fixture(
#     params=[
#         IDTypesParams(
#             input_id="00000000-0000-0000-0000-000000000000",
#             expected=nullcontext(),
#         ),
#         IDTypesParams(
#             input_id="wrong_uuid",
#             expected=pytest.raises(ValueError),
#         ),
#         IDTypesParams(
#             input_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
#             expected=nullcontext(),
#         ),
#     ]
# )
# def type_id_params(request: pytest.FixtureRequest) -> IDTypesParams:
#     return request.param


# @dataclass
# class IDExistingParams:
#     id: uuid.UUID
#     user_id: uuid.UUID
#     expected: Any


# @pytest.fixture(
#     params=[
#         IDExistingParams(
#             id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
#             user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
#             expected=nullcontext(),
#         ),
#         IDExistingParams(
#             id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
#             user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
#             expected=pytest.raises(NotPermittedError),
#         ),
#         IDExistingParams(
#             id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
#             user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
#             expected=pytest.raises(RecordNotFoundError),
#         ),
#     ]
# )
# def param_ids(request: pytest.FixtureRequest) -> IDExistingParams:
#     return request.param
