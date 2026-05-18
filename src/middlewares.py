from collections.abc import Awaitable, Callable
import structlog
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from waygate.fastapi import WaygateMiddleware
from src.config import settings
from src.repositories.crud.db import async_session_factory
from src.utils.rate_limit import rate_limit_engine

logger = structlog.get_logger()


type CallNext = Callable[[Request], Awaitable[Response]]


async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time: float = time.perf_counter() - start_time
    response.headers["x-process-time"] = str(process_time)
    logger.info(
        "Request handling time. %s" % round(process_time, 4),
        # extra={"process_time": round(process_time, 4)},
    )
    return response


async def db_session_middleware(
    request: Request,
    call_next: CallNext,
) -> Response:
    try:
        session = async_session_factory()
        request.state.db = session
        response = await call_next(request)
    except Exception as e:
        raise e from None
    finally:
        await request.state.db.close()
    return response


def register_middlewares(app: FastAPI) -> None:


    engine = rate_limit_engine.make_engine()
    app.add_middleware(WaygateMiddleware, engine=engine)

    app.middleware("http")(db_session_middleware)
    app.middleware("http")(add_process_time_header)

    # TODO: add middleware for CORS parsed fro env
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "OPTIONS",
            "DELETE",
            "PATCH",
            "PUT",
            "HEAD",
        ],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Authorization",
            "X-Requested-With",
            "x-process-time",
        ],
    )
