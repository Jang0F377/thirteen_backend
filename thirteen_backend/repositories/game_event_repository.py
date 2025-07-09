from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from thirteen_backend.models.game_event_model import GameEvent, GameEventType


async def create_game_event(
    *,
    game_id: str,
    sequence: int,
    turn: int,
    event_type: GameEventType,
    payload: dict[str, Any] | None = None,
    ts: datetime | None = None,
) -> GameEvent:
    """Persist a new ``GameEvent`` for the provided game session.

    Parameters
    ----------
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

    Returns
    -------
    GameEvent
        The newly-created ``GameEvent`` instance
    """
    event = GameEvent(
        id=uuid4(),
        seq=sequence,
        turn=turn,
        type=event_type,
        payload=payload,
        ts=ts or datetime.now(timezone.utc),
        game_id=game_id,
    )

    return event
