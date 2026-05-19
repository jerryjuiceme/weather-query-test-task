from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from src.repositories.crud.db import async_session_factory
from src.config import settings
from fastapi_users.authentication.strategy.jwt import JWTStrategy
from src.api.dependencies.auth.users import get_users_db
from src.api.dependencies.auth.user_manager import get_user_manager

import contextlib

get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        credentials = OAuth2PasswordRequestForm(
            username=str(email),
            password=str(password),
        )
        async with async_session_factory() as session:
            async with get_users_db_context(session) as users_db:
                async with get_user_manager_context(users_db) as user_manager:
                    user = await user_manager.authenticate(credentials)

                    if user is None:
                        return False

                    if not user.is_active or not user.is_superuser:
                        return False
                    strategy = JWTStrategy(
                        secret=settings.secret_key,
                        lifetime_seconds=settings.access_token.lifetime_seconds,
                    )

                    token = await strategy.write_token(user)

                    request.session.update({"token": token})

                    return True

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        async with async_session_factory() as session:
            async with get_users_db_context(session) as users_db:
                async with get_user_manager_context(users_db) as user_manager:
                    strategy = JWTStrategy(
                        secret=settings.secret_key,
                        lifetime_seconds=settings.access_token.lifetime_seconds,
                    )

                    try:
                        user = await strategy.read_token(token, user_manager)
                    except Exception:
                        return False

                    if not user:
                        return False

                    user = await user_manager.get(user.id)
                    if not user or not user.is_active or not user.is_superuser:
                        return False

        return True


authentication_backend = AdminAuth(secret_key=settings.secret_key)
