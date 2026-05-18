import structlog
import stamina
from stamina.instrumentation import RetryDetails

logger = structlog.get_logger("retry")


def log_retry(details: RetryDetails):
    service_name = None

    if details.args:
        self_obj = details.args[0]
        service_name = self_obj.__class__.__name__

    logger.warning(
        "Retry",
        retry_num=details.retry_num,
        service=service_name,
        target=details.name,
        waited=details.waited_so_far,
        exc_info=details.caused_by,
    )


def setup_retry_logging():
    stamina.instrumentation.set_on_retry_hooks([log_retry])
    logger.info("Retry logging enabled")
