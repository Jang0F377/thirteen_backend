import asyncio
from uuid import UUID

from redis.asyncio import Redis

from thirteen_backend.domain.game import Game
from thirteen_backend.logger import LOGGER
from thirteen_backend.repositories.session_state_repository import (
    increment_session_sequencer,
    set_session_state,
)
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import make_state_sync


async def persist_and_broadcast(
    *,
    redis_client: Redis,
    session_id: str,
    engine: Game,
) -> int:
    LOGGER.info(
        "Persisting and broadcasting game state",
        extra={"session_id": session_id},
    )
    set_success, new_seq = await asyncio.gather(
        set_session_state(
            redis_client=redis_client,
            game_id=session_id,
            game_state=engine,
        ),
        increment_session_sequencer(redis_client=redis_client, game_id=session_id),
    )
    if not set_success or new_seq is None:
        raise RuntimeError("Failed to set session state")

    await websocket_manager.broadcast(
        session_id=session_id,
        message=make_state_sync(
            session_id=session_id,
            game=engine,
            seq=new_seq,
        ),
    )
    return new_seq
