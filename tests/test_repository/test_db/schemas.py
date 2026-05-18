from src.schemas.base import CreateBaseModel, ReadBaseModel
import uuid


class TempTestCreate(CreateBaseModel):
    str_column: str
    int_column: int
    float_column: float
    bool_column: bool


class TempTestRead(ReadBaseModel):
    id: uuid.UUID
    str_column: str
    int_column: int
    float_column: float
    bool_column: bool
