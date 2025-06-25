from uuid import UUID
import json

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
    *, context: APIRequestContext, game_id: UUID, game_state: GameState
) -> bool:
    """
    Set the game state for a given game session.
    """
    state_key = _make_session_state_key(game_id)

    return await context.redis_client.setex(
        name=state_key,
        time=60 * 60 * 24,
        value=json.dumps(game_state.to_dict()),
    )


async def push_session_event(
    *, context: APIRequestContext, game_id: UUID, event: GameEvent
) -> None:
    """
    Push a game event to the session event queue.
    """
    event_key = _make_session_event_key(game_id)
    await context.redis_client.lpush(
        event_key,
        json.dumps(event.to_dict()),
    )


async def increment_session_sequencer(
    *,
    context: APIRequestContext,
    game_id: UUID,
) -> int:
    """
    Increment the session sequencer.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    return await context.redis_client.incr(name=sequencer_key)
