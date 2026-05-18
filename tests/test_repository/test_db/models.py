"""
Module containing test models.
"""

import uuid

from sqlalchemy import Boolean, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from src.repositories.crud.db import ModelBase


class CrudTestModel(ModelBase):
    """
    Test model for repository testing.
    """

    __tablename__ = "crud_test_model"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    str_column: Mapped[str] = mapped_column(String(length=100), nullable=False)
    int_column: Mapped[int] = mapped_column(Integer, nullable=False)
    float_column: Mapped[float] = mapped_column(Float, nullable=False)
    bool_column: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # metadata = test_metadata = MetaData(naming_convention=settings.db.naming_convention)
