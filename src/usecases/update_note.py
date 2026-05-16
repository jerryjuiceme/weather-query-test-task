import uuid
from typing import Annotated, Any

from fastapi.params import Depends

from src.exceptions import RecordNotFoundError
from src.repositories.crud.transaction_manager import (
    TransactionService,
    get_transaction_service,
)
from src.schemas.note import NoteUpdate, NoteUpdateRequest
from src.services.db import NoteService, NoteServiceDep


class UpdateNote:
    def __init__(
        self,
        transaction_service: TransactionService,
        note_service: NoteService,
    ) -> None:
        self.note_service = note_service
        self.transaction_service = transaction_service

    async def __call__(self, id: uuid.UUID, note_update: NoteUpdateRequest) -> Any:
        async with self.transaction_service.begin():
            updated_note = note_update.model_dump()
            updated_note["id"] = id
            new_note = NoteUpdate.model_validate(updated_note)
            note = await self.note_service.get_note(id=id)
            if note is None:
                raise RecordNotFoundError(detail="Note not found")
            return await self.note_service.update(new_note)


async def get_update_note_usecase(
    note_service: NoteServiceDep,
    transaction_service: Annotated[
        TransactionService, Depends(get_transaction_service)
    ],
):
    return UpdateNote(transaction_service, note_service)
