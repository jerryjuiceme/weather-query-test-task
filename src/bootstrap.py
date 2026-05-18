from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api import api_router as main_api_router
from src.config import settings
from src.error_handlers import register_errors_handlers
from src.loggers import set_logging
from src.middlewares import register_middlewares
from src.repositories.cache import cache_manager
from src.repositories.crud.db import dispose
from src.utils.retry import setup_retry_logging
from src.utils import name_to_snake
from src.repositories.http import HttpRepository
from src.utils.rate_limit import rate_limit_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    set_logging(settings=settings)
    setup_retry_logging()
    await cache_manager.connect()
    rate_limit_engine.log_connect()
    async with HttpRepository() as http_repository:
        app.state.weather_repo = http_repository
        # startup
        yield
        # shutdown
    await cache_manager.disconnect()
    await dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        default_response_class=JSONResponse,
        title=name_to_snake(settings.project_name),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/docs.json",
        version=settings.version,
    )

    app.include_router(main_api_router)
    # admin = Admin(
    #     app=app,
    #     engine=aen,
    #     authentication_backend=authentication_backend,
    #     logo_url=settings.admin.logo_url,
    #     favicon_url=settings.admin.favicon_url,
    # )
    # register_admin_views(admin)
    register_errors_handlers(app)
    register_middlewares(app)
    return app
