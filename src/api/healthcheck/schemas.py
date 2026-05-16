from pydantic.dataclasses import dataclass
from pydantic import BaseModel, ConfigDict


@dataclass
class LivenessResponseSchema:
    status: str = "healthy"


class ServiceStatusSchema(BaseModel):
    service: str
    status: str


class ReadinessResponseSchema(BaseModel):
    status: str = "healthy"
    service: list[ServiceStatusSchema | None] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)
