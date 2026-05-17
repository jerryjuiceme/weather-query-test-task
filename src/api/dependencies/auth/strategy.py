from typing import Callable


from fastapi_users.authentication.strategy.jwt import JWTStrategy

from src.config import settings


class AppStrategy:
    @staticmethod
    def get_jwt_strategy() -> JWTStrategy:
        return JWTStrategy(
            secret=settings.secret_key,
            lifetime_seconds=settings.access_token.lifetime_seconds,
        )

    def make_a_strategy(self) -> Callable:
        return self.get_jwt_strategy

    @property
    def name(self) -> str:
        return "jwt"


app_strategy = AppStrategy()


__all__ = [
    "app_strategy",
]
