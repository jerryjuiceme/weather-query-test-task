from httpx import AsyncClient

CITY = "Berlin"
NONEXISTENT_CITY = "NonExistentCityXYZ"


class TestWeatherApi:
    # GET /api/v1/weather

    async def test_get_weather_unauthorized(
        self, async_client: AsyncClient, prepare_database
    ):
        response = await async_client.get("/api/v1/weather", params={"city": CITY})
        assert response.status_code == 401

    async def test_get_weather_not_from_cache(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        # First request — should not be cached
        response = await async_client.get(
            "/api/v1/weather",
            params={"city": CITY},
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        assert response.json()["isFromCache"] is False

    async def test_get_weather_from_cache(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):

        await async_client.get(
            "/api/v1/weather",
            params={"city": CITY},
            headers={"Authorization": auth_token},
        )
        # Second request — should be served from cache
        response = await async_client.get(
            "/api/v1/weather",
            params={"city": CITY},
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        assert response.json()["isFromCache"] is True


class TestWeatherRateLimit:
    """
    GET /api/v1/weather Rate Limit
    Using separate test class due to rate limit is per class flush
    """

    async def test_get_weather_rate_limit(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        # Rate limit in test env 20 req/min; 21th must return 429
        for _ in range(20):
            await async_client.get(
                "/api/v1/weather",
                params={"city": CITY},
                headers={"Authorization": auth_token},
            )
        response = await async_client.get(
            "/api/v1/weather",
            params={"city": CITY},
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 429
