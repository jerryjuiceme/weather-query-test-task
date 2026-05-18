from collections.abc import Awaitable, Callable
import structlog
import uuid
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from waygate.fastapi import WaygateMiddleware
from src.config import settings
from src.repositories.crud.db import async_session_factory
from src.utils import rate_limit_engine, get_http_status, get_http_status_group

logger = structlog.get_logger()


type CallNext = Callable[[Request], Awaitable[Response]]


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


async def per_request_middleware(request: Request, call_next):
    # ------- bind contextvars for all requests -------
    structlog.contextvars.clear_contextvars()

    request_id = str(uuid.uuid4())
    route = request.scope.get("route")
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        route=route.path if route else request.url.path,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # ------- log request process time ---------
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    # ------- log request info ---------
    logger.info(
        "request_completed",
        status_code=response.status_code,
        status=get_http_status(response.status_code),
        status_group=get_http_status_group(response.status_code),
        duration_ms=round(process_time * 1000, 2),
    )

    return response


def register_middlewares(app: FastAPI) -> None:

    engine = rate_limit_engine.make_engine()
    app.add_middleware(WaygateMiddleware, engine=engine)

    app.middleware("http")(db_session_middleware)
    app.middleware("http")(per_request_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=[
            "GET",
            # Other methods for admin
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "X-Request-ID",
        ],
        expose_headers=[
            "X-Process-Time",
            "X-Request-ID",
        ],
    )
