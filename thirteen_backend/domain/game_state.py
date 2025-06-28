import uuid
from dataclasses import dataclass, field

from thirteen_backend.domain.player import Player


@dataclass(slots=True)
class GameState:
    players_state: list[Player]
    current_turn_order: list[int]
    turn_number: int
    who_has_power: int | None
    game_id: str

    def to_dict(self):
        return {
            "players_state": [p.to_dict() for p in self.players_state],
            "current_turn_order": self.current_turn_order,
            "turn_number": self.turn_number,
            "who_has_power": self.who_has_power,
            "game_id": self.game_id,
        }
