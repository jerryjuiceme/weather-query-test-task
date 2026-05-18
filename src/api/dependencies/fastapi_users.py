import structlog

from typing import Annotated
import uuid
from fastapi import Depends
from fastapi_users import FastAPIUsers

from src.repositories.crud.models import User
from src.api.dependencies.auth.user_manager import get_user_manager
from src.api.dependencies.auth.backend import authentication_backend
from src.schemas.user import UserRead

logger = structlog.get_logger()
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [authentication_backend]
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


def get_current_active_user(user: Annotated[User, Depends(current_active_user)]):
    structlog.contextvars.bind_contextvars(
        user_id=user.id,
        user_email=user.email,
        is_superuser=user.is_superuser,
    )
    return UserRead.model_validate(user)


def get_current_active_superuser(
    user: Annotated[User, Depends(current_active_superuser)],
):

    return UserRead.model_validate(user)


CurrentUserDep = Annotated[UserRead, Depends(get_current_active_user)]
CurrentSuperuserDep = Annotated[UserRead, Depends(get_current_active_superuser)]
