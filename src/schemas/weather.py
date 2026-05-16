from typing import Literal

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, field_serializer
from .base import CreateBaseModel, ReadBaseModel
from pydantic.alias_generators import to_camel
from datetime import datetime
import uuid


class WeatherCreate(CreateBaseModel):
    user_id: uuid.UUID
    city_name: str
    temperature: float
    description: str | None
    humidity: int
    units: Literal["metric", "imperial"]
    is_from_cache: bool = False


class WeatherRead(ReadBaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    city_name: str
    temperature: float
    description: str | None
    humidity: int
    units: Literal["metric", "imperial"]
    is_from_cache: bool = False
    created_at: datetime


class WeatherOutputMessage(BaseModel):

    city_name: str
    temperature: float
    description: str | None
    humidity: int
    units: Literal["metric", "imperial"]
    is_from_cache: bool
    created_at: datetime = Field(serialization_alias="requested_at")

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        populate_by_name=True,
        from_attributes=True,
    )

    @field_serializer("created_at", when_used="json")
    def serialize_process_datetime(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
