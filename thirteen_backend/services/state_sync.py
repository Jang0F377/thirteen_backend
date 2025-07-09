import asyncio
from uuid import UUID

from redis.asyncio import Redis

from thirteen_backend.domain.game import Game
from thirteen_backend.logger import LOGGER
from thirteen_backend.repositories import game_event_repository
from thirteen_backend.repositories.session_state_repository import (
    increment_session_sequencer,
    set_session_state,
    push_session_event,
)
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import make_state_sync
from thirteen_backend.models.game_event_model import GameEventType
from thirteen_backend.types import Play


async def persist_and_broadcast(
    *,
    redis_client: Redis,
    session_id: str,
    current_sequence: int,
    play: Play | None,
    engine: Game,
) -> int:
    LOGGER.info(
        "Persisting and broadcasting game state",
        extra={"session_id": session_id},
    )
    event_type = GameEventType.PLAY if play else GameEventType.PASS
    event = await game_event_repository.create_game_event(
        game_id=session_id,
        sequence=current_sequence,
        turn=engine.state.turn_number,
        event_type=event_type,
        payload=engine.state.to_full_dict(),
    )
    set_success, new_seq, _ = await asyncio.gather(
        set_session_state(
            redis_client=redis_client,
            game_id=session_id,
            game_state=engine,
        ),
        increment_session_sequencer(redis_client=redis_client, game_id=session_id),
        push_session_event(
            redis_client=redis_client,
            game_id=session_id,
            event=event,
        ),
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
