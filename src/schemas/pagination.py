from __future__ import annotations
from typing import Generic, Literal, TypeVar
from datetime import datetime

from pydantic import BaseModel, Field


class PaginationRequestSchema(BaseModel):
    """
    Schema for pagination
    """

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    sort: str | None = None
    order_by: Literal["asc", "desc"] = "asc"

    def to_pagination_schema(self) -> PaginationSchema:
        """
        Convert to a pagination schema using limit and offset.
        """
        return PaginationSchema(
            limit=self.page_size, offset=(self.page - 1) * self.page_size
        )


T = TypeVar("T")


class PaginationSchema(BaseModel):
    """
    Pagination schema using limit and offset.
    """

    limit: int
    offset: int


class PaginationResultSchema(BaseModel, Generic[T]):
    """
    Schema for pagination result
    """

    objects: list[T]
    filtered_count: int
    total_count: int


class FilterSchema(BaseModel):
    city_substring: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
