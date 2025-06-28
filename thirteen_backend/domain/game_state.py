import uuid
from dataclasses import dataclass, field

from thirteen_backend.domain.player import Human, Bot


@dataclass(slots=True)
class GameState:
    players_state: list[Human | Bot]
    current_turn_order: list[int]
    turn_number: int
    who_has_power: int | None
    game_id: str

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_public_dict(self) -> dict:
        """Return representation intended for **clients** – bot hands masked."""
        return {
            "players_state": [p.to_public_dict() for p in self.players_state],
            "current_turn_order": self.current_turn_order,
            "turn_number": self.turn_number,
            "who_has_power": self.who_has_power,
            "game_id": self.game_id,
        }

    def to_full_dict(self) -> dict:
        """Return **internal** representation – includes bot hands."""
        return {
            "players_state": [p.to_full_dict() for p in self.players_state],
            "current_turn_order": self.current_turn_order,
            "turn_number": self.turn_number,
            "who_has_power": self.who_has_power,
            "game_id": self.game_id,
        }
