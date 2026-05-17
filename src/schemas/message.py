"""
Api Base Message Module
"""

from typing import Generic, TypeVar

from pydantic import AliasGenerator, ConfigDict
from pydantic.alias_generators import to_camel

from .base import OutputApiSchema

T = TypeVar("T")


class ApiOutputMessage(OutputApiSchema, Generic[T]):
    """
    Base Message schema
    """

    data: T
    status: str

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        populate_by_name=True,
        from_attributes=True,
    )
