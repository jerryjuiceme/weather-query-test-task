from typing import (
    TYPE_CHECKING,
    Annotated,
    Callable,
)

from fastapi import Depends
from fastapi_users.authentication.strategy.db import DatabaseStrategy

from fastapi_users.authentication.strategy.jwt import JWTStrategy

from src.config import settings
from src.api.dependencies.auth.access_token import get_access_tokens_db

if TYPE_CHECKING:
    from src.repositories.crud.models import AccessToken
    from fastapi_users.authentication.strategy.db import AccessTokenDatabase


class AppStrategy:
    @staticmethod
    def get_database_strategy(
        access_tokens_db: Annotated[
            "AccessTokenDatabase[AccessToken]",
            Depends(get_access_tokens_db),
        ],
    ) -> DatabaseStrategy:
        return DatabaseStrategy(
            database=access_tokens_db,
            lifetime_seconds=settings.access_token.lifetime_seconds,
        )

    @staticmethod
    def get_jwt_strategy() -> JWTStrategy:
        return JWTStrategy(
            secret=settings.secret_key,
            lifetime_seconds=settings.access_token.lifetime_seconds,
        )

    def make_a_strategy(self) -> Callable:
        if settings.strategy == "jwt":
            return self.get_jwt_strategy
        return self.get_database_strategy

    @property
    def name(self) -> str:
        if settings.strategy == "jwt":
            return "jwt"
        return "access-tokens-db"


app_strategy = AppStrategy()


__all__ = [
    "app_strategy",
]
