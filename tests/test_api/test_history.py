from httpx import AsyncClient
import pytest

CITY = "Berlin"
NONEXISTENT_CITY = "NonExistentCityXYZ"


class TestHistoryApi:
    # GET /api/v1/history/

    async def test_get_history_unauthorized(
        self, async_client: AsyncClient, prepare_database
    ):
        response = await async_client.get("/api/v1/history/")
        assert response.status_code == 401

    async def test_get_history(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.get(
            "/api/v1/history/",
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    async def test_get_history_filter_by_city(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.get(
            "/api/v1/history/",
            params={"city": "Berlin"},
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total_count"] == 1

    async def test_get_history_filter_by_date_range(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.get(
            "/api/v1/history/",
            params={"date_from": "2025-01-01", "date_to": "2026-12-31"},
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @pytest.mark.parametrize(
        "params, expected_status",
        [
            ({"page": 1, "page_size": 10, "order_by": "asc"}, 200),
            ({"page": 1, "page_size": 10, "order_by": "desc"}, 200),
            ({"page": 1, "page_size": 10, "order_by": "invalid"}, 422),
            ({"page": -1, "page_size": 10, "order_by": "asc"}, 422),
            ({"page": 1, "page_size": 0, "order_by": "asc"}, 422),
        ],
    )
    async def test_get_history_pagination_params(
        self,
        async_client: AsyncClient,
        auth_token: str,
        params: dict,
        expected_status: int,
        prepare_database,
    ):
        response = await async_client.get(
            "/api/v1/history/",
            params=params,
            headers={"Authorization": auth_token},
        )
        assert response.status_code == expected_status

    async def test_export_history_city_not_found(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.get(
            "/api/v1/history/export",
            params={"city": NONEXISTENT_CITY},
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 404
