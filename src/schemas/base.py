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


class ReadBaseModel(BaseModel):
    """
    Schema for reading models
    """

    id: uuid.UUID


class OutputApiSchema(BaseModel):
    """
    Output API schema
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        )
    )
