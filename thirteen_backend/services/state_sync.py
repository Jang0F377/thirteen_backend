import asyncio
from uuid import UUID

from redis.asyncio import Redis

from thirteen_backend import metrics
from thirteen_backend.domain.game import Game
from thirteen_backend.logger import LOGGER
from thirteen_backend.models.game_event_model import GameEventType
from thirteen_backend.repositories import game_event_repository
from thirteen_backend.repositories.session_state_repository import (
    increment_session_sequencer,
    push_session_event,
    set_session_state,
)
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import make_state_sync
from thirteen_backend.types import Play


async def persist_and_broadcast(
    *,
    redis_client: Redis,
    session_id: str,
    play: Play | None,
    engine: Game,
) -> int:
    # Bump the sequencer first so we know the *new* sequence
    new_seq = await increment_session_sequencer(
        redis_client=redis_client, game_id=session_id
    )

    # Create the GameEvent using *new_seq*
    event = await game_event_repository.create_game_event(
        game_id=session_id,
        sequence=new_seq,
        turn=engine.state.turn_number,
        event_type=GameEventType.PLAY if play else GameEventType.PASS,
        payload=engine.state.to_full_dict(),
    )

    # Persist state + push event in parallel
    set_ok, _ = await asyncio.gather(
        set_session_state(
            redis_client=redis_client,
            game_id=session_id,
            game_state=engine,
        ),
        push_session_event(
            redis_client=redis_client,
            game_id=session_id,
            event=event,
        ),
    )

    if not set_ok:
        raise RuntimeError("Failed to save game state")

    # Metrics
    metrics.increment_game_event(event_type=event.type)

    # Broadcast
    await websocket_manager.broadcast(
        session_id=session_id,
        message=make_state_sync(
            session_id=session_id,
            seq=new_seq,
            game=engine,
        ),
    )

    return new_seq
