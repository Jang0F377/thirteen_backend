from enum import StrEnum

from pydantic import BaseModel


class ErrorCode(StrEnum):
    INTERNAL_SERVER_ERROR = "internal_server_error"


class Error(BaseModel):
    user_feedback: str
    error_code: ErrorCode
