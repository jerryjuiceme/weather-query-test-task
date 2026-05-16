from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from src.repositories.crud.db import ModelBase as Base
from .mixins import UUIDIdPkMixin
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from . import User


class WeatherHistory(UUIDIdPkMixin, Base):
    __tablename__ = "weather_history"

    city_name: Mapped[str] = mapped_column(nullable=False, index=True)
    temperature: Mapped[float] = mapped_column(nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    description: Mapped[str] = mapped_column(nullable=True)

    humidity: Mapped[int]
    units: Mapped[Literal["metric", "imperial"]] = mapped_column(
        String(10), nullable=False, default="metric"
    )
    is_from_cache: Mapped[bool] = mapped_column(nullable=False, default=False)
    user: Mapped["User"] = relationship(back_populates="weather_history")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __str__(self) -> str:
        return f"Request for {self.city_name!r} created: {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def __repr__(self):
        return f"WeatherHistory(id={self.id}, city_name={self.city_name})"
