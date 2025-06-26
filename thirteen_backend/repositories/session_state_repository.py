from uuid import UUID
import json

from redis.asyncio.client import Pipeline
from thirteen_backend.context import APIRequestContext
from thirteen_backend.domain.game_state import GameState
from thirteen_backend.models.game_event_model import GameEvent


def _make_session_state_key(game_id: UUID) -> str:
    return f"session:{game_id}:state"


def _make_session_event_key(game_id: UUID) -> str:
    return f"session:{game_id}:events"


def _make_session_sequencer_key(game_id: UUID) -> str:
    return f"session:{game_id}:seq"


async def set_session_state(
    *, pipe: Pipeline, game_id: UUID, game_state: GameState
) -> bool:
    """
    Set the game state for a given game session.
    """
    state_key = _make_session_state_key(game_id)

    return await pipe.setex(
        name=state_key,
        time=60 * 60 * 24,
        value=json.dumps(game_state.to_dict()),
    )


async def push_session_event(
    *, pipe: Pipeline, game_id: UUID, event: GameEvent
) -> None:
    """
    Push a game event to the session event queue.
    """
    event_key = _make_session_event_key(game_id)
    await pipe.lpush(
        event_key,
        json.dumps(event.to_dict()),
    )


async def increment_session_sequencer(
    *,
    pipe: Pipeline,
    game_id: UUID,
) -> int:
    """
    Increment the session sequencer.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    return await pipe.incr(name=sequencer_key)


async def initialize_session_sequencer(
    *,
    pipe: Pipeline,
    game_id: UUID,
    sequencer: int = 0,
) -> bool:
    """
    Set the session sequencer.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    return await pipe.setex(
        name=sequencer_key,
        time=60 * 60 * 24,
        value=sequencer,
    )
    

async def get_session_state(
    *,
    context: APIRequestContext,
    game_id: UUID,
) -> GameState | None:
    """
    Get the session state.
    """
    state_key = _make_session_state_key(game_id)
    game_state = await context.redis_client.get(name=state_key)
    if game_state is None:
        return None
    game_state_json = json.loads(game_state)
    
    return GameState(
        players_state=game_state_json["playersState"],
        current_turn_order=game_state_json["currentTurnOrder"],
        turn_number=game_state_json["turnNumber"],
        who_has_power=game_state_json["whoHasPower"],
    )


async def get_session_sequencer(
    *,
    context: APIRequestContext,
    game_id: UUID,
) -> int | None:
    """
    Get the session sequencer.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    sequencer = await context.redis_client.get(name=sequencer_key)
    if sequencer is None:
        return None
    return int(sequencer)