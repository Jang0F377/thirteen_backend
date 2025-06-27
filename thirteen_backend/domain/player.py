from dataclasses import dataclass, field
import uuid

from thirteen_backend.domain.card import Card


@dataclass(slots=True)
class Player:
    player_index: int  # 0-based seat number
    is_bot: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hand: list[Card] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "is_bot": self.is_bot,
            "player": self.player_index,
            "hand": [c.to_dict() for c in self.hand],
        }
