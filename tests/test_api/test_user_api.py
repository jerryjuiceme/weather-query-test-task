import pytest
from httpx import AsyncClient

NOT_FOUND_UUID = "00000000-0000-0000-0000-000000000000"


#  test /api/v1/auth
class TestAuth:
    # @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "form_data, status_code",
        [
            # Correct credentials → 200
            (
                {
                    "grant_type": "password",
                    "username": "superuser@example.com",
                    "password": "superpassword123",
                    "scope": "",
                    "client_id": "string",
                    "client_secret": "string",
                },
                200,
            ),
            # Wrong password → 401
            (
                {
                    "grant_type": "password",
                    "username": "superuser@example.com",
                    "password": "wrongpassword",
                    "scope": "",
                    "client_id": "string",
                    "client_secret": "string",
                },
                400,
            ),
            # Wrong username → 401
            (
                {
                    "grant_type": "password",
                    "username": "nobody@example.com",
                    "password": "superpassword123",
                    "scope": "",
                    "client_id": "string",
                    "client_secret": "string",
                },
                400,
            ),
        ],
    )
    async def test_login(
        self,
        async_client: AsyncClient,
        form_data: dict,
        status_code: int,
        prepare_database,
    ):
        response = await async_client.post(
            "/api/v1/auth/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status_code

        # Check response data
        if status_code == 200:
            body = response.json()
            assert "access_token" in body
            assert body["token_type"].lower() == "bearer"


#  test /api/v1/users/
class TestUsersApi:
    @pytest.mark.asyncio
    async def test_get_me(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200

        body = response.json()

        assert "id" in body
        assert "email" in body
        assert "is_active" in body
        assert body["is_active"] is True

    async def test_patch_me(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        payload = {
            "name": "Updated Name",
            "given_name": "Updated",
            "family_name": "Name",
        }
        response = await async_client.patch(
            "/api/v1/users/me",
            json=payload,
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Updated Name"

    async def test_get_user_by_id(
        self,
        async_client: AsyncClient,
        auth_token: str,
        registered_user_id: str,
        prepare_database,
    ):
        response = await async_client.get(
            f"/api/v1/users/{registered_user_id}",
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == registered_user_id

    async def test_get_user_by_id_not_found(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.get(
            f"/api/v1/users/{NOT_FOUND_UUID}",
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 404

    async def test_patch_user_by_id(
        self,
        async_client: AsyncClient,
        auth_token: str,
        registered_user_id: str,
        prepare_database,
    ):
        payload = {"name": "Patched", "preferred_username": "patched_user"}
        response = await async_client.patch(
            f"/api/v1/users/{registered_user_id}",
            json=payload,
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Patched"

    async def test_delete_user_by_id(
        self,
        async_client: AsyncClient,
        auth_token: str,
        registered_user_id: str,
        prepare_database,
    ):
        response = await async_client.delete(
            f"/api/v1/users/{registered_user_id}",
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 204

    async def test_delete_user_by_id_not_found(
        self, async_client: AsyncClient, auth_token: str, prepare_database
    ):
        response = await async_client.delete(
            f"/api/v1/users/{NOT_FOUND_UUID}",
            headers={"Authorization": auth_token},
        )
        assert response.status_code == 404
