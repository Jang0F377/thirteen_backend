from uuid import UUID

from thirteen_backend.domain.game_state import GameState
from thirteen_backend.models.game_event_model import GameEvent


def create_state_sync_event(
    *,
    game_id: UUID,
    sequence: int,
    turn: int,
    game_state: GameState,
) -> GameEvent:
    pass
