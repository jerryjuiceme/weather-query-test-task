"""
Base schemas module
"""

import uuid

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CreateBaseModel(BaseModel):
    """
    Schema for creating models
    """

    model_config = ConfigDict(from_attributes=True)

    # id: uuid.UUID | None = None


class UpdateBaseModel(BaseModel):
    """
    Schema for updating models
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class ReadBaseModel(BaseModel):
    """
    Schema for reading models
    """

    id: uuid.UUID


class StatusOkSchema(BaseModel):
    """
    Schema for status ok
    """

    status: str = "ok"


class InputApiSchema(BaseModel):
    """
    Input API schema
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        )
    )
    # model_config = ConfigDict(
    #     alias_generator=to_camel_case,
    #     validate_by_name=True,
    # )


class OutputApiSchema(BaseModel):
    """
    Output API schema
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        )
    )


class ErrorMessage(BaseModel):
    """Error message schema."""

    detail: str
