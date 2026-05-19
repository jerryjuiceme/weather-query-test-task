from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.repositories.crud.db import get_db_request
from src.repositories.http import get_weather_repo
from src.repositories.crud import db as db_module
from src.repositories.http.weather import HttpRepository


@pytest.fixture(scope="function")
async def async_client(
    session_factory,
    mock_weather_http_repository: HttpRepository,
):

    async def override_get_db():
        async with session_factory() as session:
            yield session

    def override_get_weather_repo():
        return mock_weather_http_repository

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = session_factory
    app.dependency_overrides[get_db_request] = override_get_db
    app.dependency_overrides[get_weather_repo] = override_get_weather_repo
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
    db_module.async_session_factory = original_factory


async def authenticated_async_client(session_factory, prepare_database):

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_request] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def auth_token(
    async_client: AsyncClient, prepare_database
) -> AsyncGenerator[str, None]:
    """
    Login and return 'Bearer <token>',
    Logout after the test.
    """
    login_data = {
        "grant_type": "password",
        "username": "superuser@example.com",
        "password": "superpassword123",
        "scope": "",
        "client_id": "string",
        "client_secret": "string",
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data,  # x-www-form-urlencoded
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert (
        response.status_code == 200
    ), f"Login failed during fixture setup: {response.text}"

    token_data = response.json()
    token = f"{token_data['token_type'].capitalize()} {token_data['access_token']}"

    yield token

    await async_client.post("/api/v1/auth/logout", headers={"Authorization": token})


@pytest.fixture(scope="function")
async def registered_user_id(
    async_client: AsyncClient, auth_token: str, prepare_database
) -> str:
    payload = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "name": "Test",
        "preferred_username": "testuser",
        "given_name": "Test",
        "family_name": "User",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return response.json()["id"]
