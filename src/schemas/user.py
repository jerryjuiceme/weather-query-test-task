import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict


class UserRead(schemas.BaseUser[uuid.UUID]):
    name: str
    preferred_username: str | None
    given_name: str | None
    family_name: str | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    name: Annotated[str, MinLen(3), MaxLen(20)]
    preferred_username: Annotated[str, MinLen(3), MaxLen(20)]
    given_name: Annotated[str, MinLen(3), MaxLen(40)]
    family_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    name: str | None = None
    preferred_username: str | None = None
    given_name: str | None = None
    family_name: str | None = None


class UserRequestUpdate(BaseModel):
    name: str | None = None
    preferred_username: str | None = None
    given_name: str | None = None
    family_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
