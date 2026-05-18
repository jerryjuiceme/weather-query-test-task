import json
from pathlib import Path

import pytest
from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src.config import settings
from src.repositories.crud.db import Base

from src.repositories.crud.models import WeatherHistory
from tests.seed_user import create_superuser
from tests.test_repository.test_db.models import CrudTestModel


@pytest.fixture(scope="session")
def session_factory(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


### Prepare database for tests ###
@pytest.fixture(scope="function")
async def prepare_database(engine, session_factory):
    uuid7_sql = _open_sql_file(
        Path(settings.base_dir) / "migrations/functions/uuid_v7/upgrade.sql"
    )

    async with engine.begin() as conn:
        await conn.execute(text(uuid7_sql))
        await conn.run_sync(Base.metadata.create_all)

    test_data = _open_mock_json("crud_test_model")
    weather_data = _open_mock_json("weather")

    async with session_factory() as session:
        await session.execute(insert(CrudTestModel).values(test_data))
        key = await create_superuser(session=session)
        weather_lst = []
        for i in weather_data:
            i["user_id"] = key
            weather_lst.append(i)
        await session.execute(insert(WeatherHistory).values(weather_lst))
        await session.commit()

    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def _open_mock_json(model: str) -> list[dict]:
    with open(
        settings.base_dir / f"tests/test_repository/test_db/seed/mock_{model}.json", "r"
    ) as json_file:
        return json.load(json_file)


def _open_sql_file(filepath: Path) -> str:
    with open(filepath, "r") as f:
        return f.read()
