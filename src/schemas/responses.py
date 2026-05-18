"""
This module is used for documenting responses only
"""

from pydantic import BaseModel
from datetime import datetime


class ErrorResponse(BaseModel):
    error: dict = {"detail": "Invalid filter request"}


class NotFoundError(BaseModel):
    error: dict = {"detail": "Not found"}


class RateLimitError(BaseModel):
    code: str
    message: str
    limit: int
    retry_after_seconds: int
    reset_at: datetime
    path: str
