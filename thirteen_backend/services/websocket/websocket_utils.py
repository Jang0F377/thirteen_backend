from datetime import datetime, timezone
import json


from thirteen_backend.domain.game import Game
from thirteen_backend.models.game_event_model import GameEventType





def make_state_sync(
    *,
    session_id: str,
    seq: int,
    game: Game
) -> str:
    """Serialise STATE_SYNC message as JSON string."""
    return json.dumps({
        "type": GameEventType.STATE_SYNC,
        "seq": seq,
        "turn": game.state.turn_number,
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "game_state": game.state.to_dict(),
    })
