import contextlib
import pytest  # noqa
from dotenv import load_dotenv
import os

load_dotenv()


def get_env_var() -> str | None:
    with contextlib.suppress(KeyError):
        return os.environ["TEST_ENV_REAL"]
    return None


TEST_ENV_REAL = get_env_var()
TEST_ENV = TEST_ENV_REAL or os.environ["TEST_ENV"]
env_fixture = (
    "tests.fixtures_testcontainer"
    if TEST_ENV == "CONTAINER"
    else "tests.fixtures_real_connections"
    # else "tests.fixtures_testcontainer"
)

pytest_plugins = [
    env_fixture,
    # "tests.fixtures_real_connections",
    "tests.fixtures_database",
    "tests.fixtures_external_api",
    "tests.test_repository.test_db.fixtures",
    "tests.test_repository.test_cache.fixtures",
    # "tests.test_service.fixtures",
    "tests.test_integration.fixtures",
    "tests.test_api.fixtures",
]
