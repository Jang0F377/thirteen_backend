import asyncio
from typing import Any

from redis.asyncio import Redis

from thirteen_backend.domain.game import Game
from thirteen_backend.logger import LOGGER
from thirteen_backend.repositories.session_state_repository import (
    get_session_sequencer,
    get_session_state,
)
from thirteen_backend.services.bot.bot_handlers import play_bots_until_human
from thirteen_backend.services.state_sync import persist_and_broadcast
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import make_state_sync


async def handle_play(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
    msg: dict[str, Any],
) -> None:
    choices = msg["payload"]
    LOGGER.info(
        "Handling play for player %s",
        player_id,
        extra={
            "session_id": session_id,
            "msg": msg,
            "choices": choices,
        },
    )

    engine, seq = await _load_engine(redis_client=redis_client, session_id=session_id)

    # TODO: Add validation/removal logic for choices here
    

    engine.state.increment_turn_number()

    await persist_and_broadcast(
        redis_client=redis_client,
        session_id=session_id,
        play=choices,
        engine=engine,
    )


async def handle_pass(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    engine, seq = await _load_engine(redis_client=redis_client, session_id=session_id)

    engine.apply_pass(player_idx=engine.state.get_player_idx_by_id(player_id=player_id))

    await persist_and_broadcast(
        redis_client=redis_client,
        session_id=session_id,
        play=None,
        engine=engine,
    )

    await play_bots_until_human(
        redis_client=redis_client,
        engine=engine,
        seq=seq,
    )


async def handle_ready(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    # TODO: This will be implemented in the future
    LOGGER.info("This will be implemented in the future")


async def handle_ping(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    # TODO: This will be implemented in the future
    LOGGER.info("This will be implemented in the future")


async def handle_resync_request(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
    conn_id: str,
) -> None:
    LOGGER.info(
        "Handling resync request",
        extra={"session_id": session_id, "player_id": player_id, "conn_id": conn_id},
    )

    game_state, seq = await asyncio.gather(
        get_session_state(redis_client=redis_client, game_id=session_id),
        get_session_sequencer(redis_client=redis_client, game_id=session_id),
    )
    if game_state is None or seq is None:
        raise ValueError("Game state or sequencer not found")

    await websocket_manager.send_to(
        session_id=session_id,
        conn_id=conn_id,
        message=make_state_sync(
            session_id=session_id,
            seq=seq,
            game=game_state,
        ),
    )


async def _load_engine(
    *,
    redis_client: Redis,
    session_id: str,
) -> tuple[Game, int]:
    game_state, seq = await asyncio.gather(
        get_session_state(redis_client=redis_client, game_id=session_id),
        get_session_sequencer(redis_client=redis_client, game_id=session_id),
    )
    if game_state is None or seq is None:
        raise ValueError("Game state or sequencer not found")
    return game_state, seq
