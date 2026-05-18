from pathlib import Path
from typing import AsyncGenerator
import pytest
import json

from .repository import TempTestRepository
from src.repositories.crud import WeatherRepository


@pytest.fixture(scope="function")
async def test_repository(
    prepare_database, session_factory
) -> AsyncGenerator[TempTestRepository, None]:
    async with session_factory() as session:
        yield TempTestRepository(session)


@pytest.fixture(scope="function")
async def test_weather_repository(
    prepare_database, session_factory
) -> AsyncGenerator[WeatherRepository, None]:
    async with session_factory() as session:
        yield WeatherRepository(session)


@pytest.fixture(scope="class")
async def test_data_params() -> list[dict]:
    test_data = _open_mock_json("crud_test_model")
    return test_data


def _open_mock_json(model: str) -> list[dict]:
    with open(
        f"tests/test_repository/test_db/seed/mock_{model}.json", "r"
    ) as json_file:
        return json.load(json_file)


def _open_sql_file(filepath: Path) -> str:
    with open(filepath, "r") as f:
        return f.read()
