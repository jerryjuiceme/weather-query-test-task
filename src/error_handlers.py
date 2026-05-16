import structlog
from asyncpg.exceptions._base import InterfaceError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, OperationalError

from src.exceptions import (
    UseCaseBaseError,
    UserAlreadyExistsException,
)

logger = structlog.get_logger()


def register_errors_handlers(app: FastAPI) -> None:

    #######################
    ### Pydantic errors ###
    #######################

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

    # @app.exception_handler(RequestValidationError)
    # async def handle_request_validation_error(
    #     request: Request,
    #     exc: RequestValidationError,
    # ) -> JSONResponse:
    #     logger.warning("Request validation error: %s", exc.errors(), exc_info=exc)
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content={
    #             "message": "Validation error. Please check your request.",
    #             "error": exc.errors(),
    #         },
    #     )

    #######################
    ### Use case errors ###
    #######################
    @app.exception_handler(UseCaseBaseError)
    async def handle_use_case_error(
        request: Request,
        exc: UseCaseBaseError,
    ) -> JSONResponse:
        logger.error("Permitted error", details=exc.detail, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "A server-side error occurred while processing your request.",
                "detail": exc.detail,
            },
        )

    #########################
    ### Connection errors ###
    #########################
    @app.exception_handler(DatabaseError)
    async def handle_db_error(
        request: Request,
        exc: DatabaseError,
    ) -> JSONResponse:
        logger.error(
            "Unhandled database error",
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )

    @app.exception_handler(OperationalError)
    async def handle_operational_error(
        request: Request,
        exc: OperationalError,
    ) -> JSONResponse:
        logger.error(
            "Database connection failed",
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "Database is temporarily unavailable. Please try again later."
            },
        )

    @app.exception_handler(ConnectionRefusedError)
    async def handle_connection_refused_error(
        request: Request,
        exc: ConnectionRefusedError,
    ) -> JSONResponse:
        logger.error(
            "Connection refused — likely DB is down",
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "Cannot connect to database server.\\"
                " Please contact support or try again later."
            },
        )

    @app.exception_handler(InterfaceError)
    async def handle_asyncpg_error(
        request: Request,
        exc: InterfaceError,
    ) -> JSONResponse:
        logger.error(
            "Database connection failed",
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "Database is temporarily unavailable. Please try again later."
            },
        )

    ###########################
    ### User already exists ###
    ###########################
    @app.exception_handler(UserAlreadyExistsException)
    async def handle_user_already_exists(
        request: Request,
        exc: UserAlreadyExistsException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": exc.detail,
            },
        )

    ########################
    ### Unhandled errors ###
    ########################

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled internal server error"
        )  # ← logging entire traceback
        logger.error("Error while processing request", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error has occurred. "
                "Our administrators have been notified.",
            },
        )
