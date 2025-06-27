from datetime import datetime
from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from thirteen_backend.adapters import postgres
from thirteen_backend.utils import api_responses
from thirteen_backend.utils.api_responses import Success

router = APIRouter(tags=["healthcheck"])


@router.get("/__healthcheck")
async def healthcheck() -> Success[dict[str, Any]]:
    return api_responses.success({"healthy": True, "time": datetime.now()})


@router.get("/__ready")
async def readiness() -> Success[None]:
    async with postgres.get_session() as session:
        await session.scalar(select(1))
    return api_responses.success(None)
