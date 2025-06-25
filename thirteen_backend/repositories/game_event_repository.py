from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from thirteen_backend.context import APIRequestContext
from thirteen_backend.models.game_event_model import GameEvent, GameEventType


async def create_game_event(
    *,
    context: APIRequestContext,
    game_id: UUID,
    sequence: int,
    turn: int,
    event_type: GameEventType,
    payload: dict[str, Any] | None = None,
    ts: datetime | None = None,
    flush_to_db: bool = True,
) -> GameEvent:
    """Persist a new ``GameEvent`` for the provided game session.

    Parameters
    ----------
    context:
        The current :class:`~thirteen_backend.context.APIRequestContext`.
    game_id:
        The identifier of the ``GameSession`` this event belongs to.
    turn:
        The turn number the event occurred on.
    event_type:
        The :class:`~thirteen_backend.models.game_event_model.GameEventType` describing the event.
    payload:
        Optional structured data associated with the event.
    ts:
        Optional timestamp of the event. If *None*, the current UTC time is used.
    flush_to_db:
        Whether to flush the event to the database. If *True*, the event will be
        added to the database session and flushed to the database. If *False*,
        the event will not be added to the database session and will not be
        flushed to the database.

    Returns
    -------
    GameEvent
        The newly-created ``GameEvent`` instance **after** it has been flushed to
        the database (i.e. it will contain a generated ``id``).
    """

    session: AsyncSession = context.db_session

    event = GameEvent(
        seq=sequence,
        turn=turn,
        type=event_type,
        payload=payload,
        ts=ts or datetime.now(timezone.utc),
        game_id=game_id,
    )
    
    if flush_to_db:
        session.add(event)
        await session.flush()

    return event
