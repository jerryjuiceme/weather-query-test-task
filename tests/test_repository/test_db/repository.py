from typing import TYPE_CHECKING

from src.repositories.crud.base import BaseRepository
from .schemas import TempTestCreate, TempTestRead
from .models import CrudTestModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TempTestRepository(BaseRepository[CrudTestModel, TempTestRead, TempTestCreate]):
    model = CrudTestModel
    read_schema = TempTestRead
    create_schema = TempTestCreate

    def __init__(self, session: "AsyncSession") -> None:
        super().__init__(session)
