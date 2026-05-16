from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    provider_asyncpg: str = "postgresql+asyncpg"
    provider_psycopg: str = "postgresql+psycopg_async"

    @property
    def DATABASE_URL_async(self) -> str:
        return f"{self.provider_asyncpg}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # api/v1/auth/login
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        # return path[1:]
        return path.removeprefix("/")


class Cache(BaseModel):
    prefix: str = "fastapi-boilerplate"
    ttl: int = int(60)


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    retry_db: int = 1

    @property
    def retry_dsn(self) -> RedisDsn:
        return RedisDsn(f"redis://{self.host}:{self.port}/{self.retry_db}")

    @property
    def dsn(self) -> RedisDsn:
        return RedisDsn(f"redis://{self.host}:{self.port}/{self.db}")


class S3(BaseModel):
    endpoint: str
    port: int
    aws_secret_access_key: str
    aws_access_key_id: str
    bucket: str
    secure: bool


class Storage(BaseModel):
    provider: Literal["s3"] = "s3"
    s3: S3


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class Admin(BaseModel):
    logo_url: str
    favicon_url: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(BASE_DIR / ".env.sample"),
            str(BASE_DIR / ".env"),
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="allow",
    )

    # ---------- api ----------
    api: ApiPrefix = ApiPrefix()

    # ---------- database ----------
    db: DatabaseConfig

    # ---------- auth ----------
    strategy: Literal["jwt", "db"] = "jwt"
    access_token: AccessToken
    first_superuser_email: str
    first_superuser_name: str
    first_superuser_password: str

    # ---------- cache ----------
    cache: Cache = Cache()
    redis: Redis

    # ---------- app ----------
    base_dir: Path = BASE_DIR
    env: Literal["TEST", "DEV", "PROD"] = "DEV"
    project_name: str
    base_url: str
    secret_key: str
    cors_origins: list[str]
    version: str
    debug: bool = True  # Reload on change

    # ---------- admin ----------
    admin: Admin


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
