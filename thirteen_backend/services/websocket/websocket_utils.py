from datetime import datetime, timezone
from uuid import UUID, uuid4

from thirteen_backend.domain.game_state import GameState
from thirteen_backend.models.game_event_model import GameEvent, GameEventType


def create_state_sync_event(
    *,
    game_id: UUID,
    sequence: int,
    turn: int,
    game_state: GameState,
) -> GameEvent:
    state_sync_event = GameEvent(
        id=uuid4(),
        seq=sequence,
        turn=turn,
        type=GameEventType.STATE_SYNC,
        payload=game_state.to_dict(),
        ts=datetime.now(timezone.utc),
        game_id=game_id,
    )
    
    return state_sync_event
