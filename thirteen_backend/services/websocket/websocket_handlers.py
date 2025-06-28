import asyncio
from typing import Any

from redis.asyncio import Redis

from thirteen_backend.domain.game import Game
from thirteen_backend.repositories.session_state_repository import (
    get_session_sequencer,
    get_session_state,
    increment_session_sequencer,
    set_session_state,
)
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import make_state_sync


async def handle_play(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
    msg: dict[str, Any],
) -> None:
    pass


async def handle_pass(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    pass


async def handle_ready(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    pass


async def handle_ping(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    pass


async def handle_resync_request(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
    conn_id: str,
) -> None:
    pass


async def _load_engine(
    *,
    redis_client: Redis,
    session_id: str,
) -> tuple[Game, int]:
    state_raw, seq_raw = await asyncio.gather(
        get_session_state(redis_client=redis_client, game_id=session_id),
        get_session_sequencer(redis_client=redis_client, game_id=session_id),
    )
    if state_raw is None or seq_raw is None:
        raise ValueError("Game state or sequencer not found")
    return Game.from_state_dict(state_raw), int(seq_raw)


async def _save_engine(
    *,
    redis_client: Redis,
    session_id: str,
    engine: Game,
) -> None:
    set_success, new_seq = await asyncio.gather(
        set_session_state(
            redis_client=redis_client, game_id=session_id, game_state=engine
        ),
        increment_session_sequencer(redis_client=redis_client, game_id=session_id),
    )
    if not set_success or new_seq is None:
        raise ValueError("Failed to set session state")

    await websocket_manager.broadcast(
        session_id=session_id,
        message=make_state_sync(
            session_id=session_id,
            seq=new_seq,
            game=engine,
        ),
    )
