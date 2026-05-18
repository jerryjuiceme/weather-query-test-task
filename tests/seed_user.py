import contextlib
from typing import TYPE_CHECKING

from fastapi_users.exceptions import UserAlreadyExists

from src.api.dependencies.auth.user_manager import get_user_manager
from src.api.dependencies.auth.users import get_users_db
from src.authentication.user_manager import UserManager
from src.repositories.crud.models import User
from src.schemas.user import UserCreate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
    user_manager: UserManager,
    user_create: UserCreate,
) -> User:
    user = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(
    session: "AsyncSession",
    email: str = "superuser@example.com",
    username: str = "superuser",
    password: str = "superpassword123",
    is_active: bool = True,
    is_superuser: bool = True,
    is_verified: bool = True,
):
    user_create = UserCreate(
        name=username,
        email=email,
        password=password,
        preferred_username="Admin_1",
        given_name="Admin_1",
        family_name="Admin_1",
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )
    try:
        async with get_users_db_context(session) as users_db:
            async with get_user_manager_context(users_db) as user_manager:
                user = await create_user(
                    user_manager=user_manager,
                    user_create=user_create,
                )
                if user is not None:
                    return user.id

    except UserAlreadyExists:
        print("User already exists. Can't create superuser")
    except Exception as e:
        print(e)
