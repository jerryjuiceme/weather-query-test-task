import structlog
from asyncpg.exceptions._base import InterfaceError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, OperationalError

from src.exceptions import (
    CityNotFoundError,
    ExternalServiceError,
    InvalidApiKeyError,
    RateLimitError,
    SortingFieldsNotProvided,
    WeatherApiTimeoutError,
)

logger = structlog.get_logger()


def register_errors_handlers(app: FastAPI) -> None:

    ##################################
    ### Pydantic validation errors ###
    ##################################

    @app.exception_handler(ValidationError)
    async def handle_pydantic_validation_error(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        logger.warning("Request validation error", errors=exc.errors(), exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Validation error. Please check your request.",
                "error": exc.errors(),
            },
        )

    #########################
    ### Connection errors ###
    #########################
    @app.exception_handler(OperationalError)
    async def handle_db_operational_error(
        request: Request,
        exc: OperationalError,
    ) -> JSONResponse:
        logger.error(
            "Database operational error",
            path=request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )

    @app.exception_handler(DatabaseError)
    async def handle_db_error(
        request: Request,
        exc: DatabaseError,
    ) -> JSONResponse:
        logger.error("Database error", path=request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )

    @app.exception_handler(InterfaceError)
    async def handle_asyncpg_interface_error(
        request: Request,
        exc: InterfaceError,
    ) -> JSONResponse:
        logger.error("AsyncPG interface error", path=request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )

    ##########################
    ### Domain/app errors  ###
    ##########################
    @app.exception_handler(SortingFieldsNotProvided)
    async def handle_sorting_fields_not_provided(
        request: Request,
        exc: SortingFieldsNotProvided,
    ) -> JSONResponse:
        logger.info("Sorting fields not provided", path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc)},
        )

    ###########################
    ### Weather API errors  ###
    ###########################
    @app.exception_handler(CityNotFoundError)
    async def handle_city_not_found(
        request: Request,
        exc: CityNotFoundError,
    ) -> JSONResponse:
        logger.info("City not found", city=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)},
        )

    @app.exception_handler(WeatherApiTimeoutError)
    async def handle_weather_timeout(
        request: Request,
        exc: WeatherApiTimeoutError,
    ) -> JSONResponse:
        logger.warning(
            "Weather API timeout after retries",
            path=request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "message": "Weather service did not respond in time. Please try again."
            },
        )

    @app.exception_handler(ExternalServiceError)
    async def handle_external_service_error(
        request: Request,
        exc: ExternalServiceError,
    ) -> JSONResponse:
        logger.error(
            "External weather service error",
            path=request.url.path,
            detail=str(exc),
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "Weather service is temporarily unavailable. Please try again later."
            },
        )

    @app.exception_handler(InvalidApiKeyError)
    async def handle_invalid_api_key(
        request: Request,
        exc: InvalidApiKeyError,
    ) -> JSONResponse:
        logger.critical(
            "Invalid OpenWeatherMap API key — check OPENWEATHER_API_KEY env var",
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal configuration error. Please contact support."
            },
        )

    @app.exception_handler(RateLimitError)
    async def handle_rate_limit(
        request: Request,
        exc: RateLimitError,
    ) -> JSONResponse:
        logger.warning(
            "Per-IP rate limit exceeded",
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "message": "Too many requests. Please slow down and try again in a minute."
            },
            headers={"Retry-After": "60"},
        )

    ########################
    ### Unhandled errors ###
    ########################

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled internal server error")
        logger.error(
            "Unexpected error while processing request",
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error has occurred. "
                "Our administrators have been notified.",
            },
        )
