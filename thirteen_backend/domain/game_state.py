import uuid
from dataclasses import dataclass, field

from thirteen_backend.domain.player import Player


@dataclass(slots=True)
class GameState:
    players_state: list[Player]
    current_turn_order: list[int]
    turn_number: int
    who_has_power: int | None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {
            "id": self.id,
            "playersState": [p.to_dict() for p in self.players_state],
            "currentTurnOrder": self.current_turn_order,
            "turnNumber": self.turn_number,
            "whoHasPower": self.who_has_power,
        }
