"""
API response helpers for JSON data
"""

from typing import TypeVar, Generic, Literal, Optional, Any
from fastapi import status
from pydantic import BaseModel, ConfigDict
from thirteen_backend.utils import json


T = TypeVar("T")


class Success(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: Literal["success"]
    data: Optional[T]
    meta: dict[str, Any]


def format_success(content: Any, meta: dict[str, Any]):
    return {"status": "success", "data": content, "meta": meta}


def success(
    content: Any,
    status_code: int = status.HTTP_200_OK,
    headers: Optional[dict[str, Any]] = None,
    meta: Optional[dict[str, Any]] = None,
) -> Any:
    if meta is None:
        meta = {}
    data = format_success(content=content, meta=meta)
    return json.ORJSONResponse(content=data, status_code=status_code, headers=headers)


def format_error(error: Any, message: str):
    return {"status": "error", "error": error, "message": message}


def error(
    error: Any,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    headers: Optional[dict] = None,
) -> Any:
    data = format_error(error=error, message=message)
    return json.ORJSONResponse(content=data, status_code=status_code, headers=headers)
