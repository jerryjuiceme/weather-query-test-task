import structlog
from asyncpg import DeadlockDetectedError, SerializationError
import stamina
from stamina.instrumentation import RetryDetails

from sqlalchemy.exc import (
    DBAPIError,
    OperationalError,
    DisconnectionError,
    TimeoutError,
)

logger = structlog.get_logger("retry")


def log_retry(details: RetryDetails):
    service_name = None

    if details.args:
        self_obj = details.args[0]
        service_name = self_obj.__class__.__name__

    logger.warning(
        "Retry #%d | service=%s | target=%s | waited=%.2fs",
        details.retry_num,
        service_name,
        details.name,
        details.waited_so_far,
        exc_info=details.caused_by,
    )


def setup_retry_logging():
    stamina.instrumentation.set_on_retry_hooks([log_retry])
    logger.info("Retry logging enabled")
