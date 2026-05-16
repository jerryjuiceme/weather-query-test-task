import uuid

from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.repositories.crud.db import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from . import WeatherHistory
    from sqlalchemy.ext.asyncio import AsyncSession


class User(SQLAlchemyBaseUserTableUUID, Base, TimestampMixin):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    name: Mapped[str] = mapped_column(nullable=True)
    preferred_username: Mapped[str] = mapped_column(nullable=True)
    given_name: Mapped[str] = mapped_column(nullable=True)
    family_name: Mapped[str] = mapped_column(nullable=True)

    weather_history: Mapped[list["WeatherHistory"]] = relationship(
        back_populates="user"
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)

    def __repr__(self):
        # return f"email={self.email!r}, name={self.name!r}"
        return f"{self.email}"
