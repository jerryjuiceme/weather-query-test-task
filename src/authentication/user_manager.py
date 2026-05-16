from typing import Optional
import structlog
from typing import TYPE_CHECKING
import uuid
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.config import settings
from src.repositories.crud.models import User

log = logger = structlog.get_logger()

if TYPE_CHECKING:
    from fastapi import Request


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        log.warning(msg=("User %r has registered." % user.id))

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        log.warning(
            msg="User %r has forgot their password. Reset token: %s" % (user.id, token)
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        log.warning(
            msg="Verification requested for user %r. Verification token: %s"
            % (user.id, token)
        )
