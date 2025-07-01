import uuid
from dataclasses import dataclass, field

from thirteen_backend.domain.card import Card


@dataclass(slots=True)
class Human:
    player_index: int  # 0-based seat number
    is_bot: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hand: list[Card] = field(default_factory=list)
    score: int = field(default=0)
    placements: list[int] = field(default_factory=list)  # [1,3,2] means 1st, 3rd, 2nd
    bombs_played: int = field(default=0)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_public_dict(self) -> dict:
        """Return **client-safe** representation (includes full hand)."""
        return {
            "id": self.id,
            "is_bot": self.is_bot,
            "player_index": self.player_index,
            "hand": [c.to_dict() for c in self.hand],
            "hand_count": len(self.hand),
            "score": self.score,
            "placements": self.placements,
            "bombs_played": self.bombs_played,
        }

    to_full_dict = to_public_dict


@dataclass(slots=True)
class Bot:
    player_index: int  # 0-based seat number
    is_bot: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hand: list[Card] = field(default_factory=list)
    score: int = field(default=0)
    placements: list[int] = field(default_factory=list)  # [1,3,2] means 1st, 3rd, 2nd
    bombs_played: int = field(default=0)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_public_dict(self) -> dict:
        """Return representation **safe for clients** – omits the hand itself."""
        return {
            "id": self.id,
            "is_bot": self.is_bot,
            "player_index": self.player_index,
            "hand_count": len(self.hand),
            "score": self.score,
            "placements": self.placements,
            "bombs_played": self.bombs_played,
        }

    def to_full_dict(self) -> dict:
        """Return *internal* representation, including the concealed hand."""
        return {
            "id": self.id,
            "is_bot": self.is_bot,
            "player_index": self.player_index,
            "hand": [c.to_dict() for c in self.hand],
            "hand_count": len(self.hand),
            "score": self.score,
            "placements": self.placements,
            "bombs_played": self.bombs_played,
        }
