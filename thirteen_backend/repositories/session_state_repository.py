import json
from uuid import UUID

from redis.asyncio import Redis

# Domain models
from thirteen_backend.domain.game import Game
from thirteen_backend.models.game_event_model import GameEvent


def _make_session_state_key(game_id: UUID) -> str:
    """
    Construct the Redis key used to persist the *serialized* game state for
    the supplied session.

    Parameters
    ----------
    game_id:
        Unique identifier of the game session.

    Returns
    -------
    str
        Namespaced Redis key in the form ``session:{game_id}:state``.
    """
    return f"session:{game_id}:state"


def _make_session_event_key(game_id: UUID) -> str:
    """
    Construct the Redis key representing the *list* that buffers game events
    for the specified session.

    Parameters
    ----------
    game_id:
        Unique identifier of the game session.

    Returns
    -------
    str
        Namespaced Redis key in the form ``session:{game_id}:events``.
    """
    return f"session:{game_id}:events"


def _make_session_sequencer_key(game_id: UUID) -> str:
    """
    Construct the Redis key that stores the per-session sequence counter.

    Parameters
    ----------
    game_id:
        Unique identifier of the game session.

    Returns
    -------
    str
        Namespaced Redis key in the form ``session:{game_id}:seq``.
    """
    return f"session:{game_id}:seq"


async def set_session_state(
    *, redis_client: Redis, game_id: UUID, game_state: Game
) -> bool:
    """Persist the current :class:`~thirteen_backend.domain.game_state.Game`
    for the supplied session in Redis.

    The state is JSON-encoded and stored with a 24-hour TTL so that abandoned
    sessions are eventually cleaned up.

    Notes
    -----
    The provided pipeline *is not* executed by this function – callers are
    expected to invoke :pymeth:`redis.asyncio.client.Pipeline.execute` after
    staging all desired commands.

    Parameters
    ----------
    pipe:
        Active asynchronous Redis pipeline that batches the write commands.
    game_id:
        Unique identifier of the game session.
    game_state:
        The domain model instance representing the latest game state.

    Returns
    -------
    bool
        ``True`` if Redis acknowledged the ``SETEX`` command with ``OK``;
        otherwise ``False``.
    """
    state_key = _make_session_state_key(game_id)

    return await redis_client.setex(
        name=state_key,
        time=60 * 60 * 24,
        value=json.dumps(game_state.to_full_dict()),
    )


async def push_session_event(
    *, redis_client: Redis, game_id: UUID, event: GameEvent
) -> None:
    """Append a new game *event* to the Redis list that buffers session events.

    Parameters
    ----------
    pipe:
        Async Redis pipeline used to stage the ``LPUSH`` command.
    game_id:
        Unique identifier of the game session.
    event:
        The :class:`~thirteen_backend.models.game_event_model.GameEvent` to
        serialize and push onto the list.
    """
    event_key = _make_session_event_key(game_id)
    await redis_client.lpush(
        event_key,
        json.dumps(event.to_dict()),
    )


async def increment_session_sequencer(
    *,
    redis_client: Redis,
    game_id: UUID,
) -> int:
    """Atomically increment the per-session sequence counter.

    The counter is used to order events generated within a single session.

    Parameters
    ----------
    pipe:
        Redis pipeline staging the ``INCR`` command.
    game_id:
        Unique identifier of the game session.

    Returns
    -------
    int
        The *post-increment* value of the sequence counter.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    return await redis_client.incr(name=sequencer_key)


async def initialize_session_sequencer(
    *,
    redis_client: Redis,
    game_id: UUID,
    sequencer: int = 0,
) -> bool:
    """Initialise the session sequence counter in Redis.

    Called once when the game session is first created. The key is stored with
    a 24-hour TTL.

    Parameters
    ----------
    pipe:
        Redis pipeline used to stage the ``SETEX`` command.
    game_id:
        Unique identifier of the game session.
    sequencer:
        Initial value for the counter (defaults to ``0``).

    Returns
    -------
    bool
        ``True`` if Redis acknowledged the ``SETEX`` command with ``OK``.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    return await redis_client.setex(
        name=sequencer_key,
        time=60 * 60 * 24,
        value=sequencer,
    )


async def get_session_state(
    *,
    redis_client: Redis,
    game_id: UUID,
) -> Game | None:
    """Retrieve and deserialize the current game state for the given session.

    Parameters
    ----------
    context:
        The active :class:`~thirteen_backend.context.APIRequestContext` providing
        access to the shared Redis client.
    game_id:
        Unique identifier of the game session.

    Returns
    -------
    Game | None
        The reconstructed game state if present; *None* otherwise.
    """
    state_key = _make_session_state_key(game_id)
    raw_state = await redis_client.get(name=state_key)
    if raw_state is None:
        return None

    # The state is stored as a JSON string – decode and rebuild the Game.
    state_dict: dict = json.loads(raw_state)
    return Game.from_state_dict(state_dict)


async def get_session_sequencer(
    *,
    redis_client: Redis,
    game_id: UUID,
) -> int | None:
    """Return the current value of the session's sequence counter, if set.

    Parameters
    ----------
    context:
        The active request context providing a Redis connection.
    game_id:
        Unique identifier of the game session.

    Returns
    -------
    int | None
        Sequence counter value if present; *None* otherwise.
    """
    sequencer_key = _make_session_sequencer_key(game_id)
    sequencer = await redis_client.get(name=sequencer_key)
    if sequencer is None:
        return None
    return int(sequencer)
