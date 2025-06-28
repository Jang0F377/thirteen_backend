import uuid
from dataclasses import dataclass, field

from thirteen_backend.domain.card import Card


@dataclass(slots=True)
class Human:
    player_index: int  # 0-based seat number
    is_bot: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hand: list[Card] = field(default_factory=list)

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
        }

    to_full_dict = to_public_dict


@dataclass(slots=True)
class Bot:
    player_index: int  # 0-based seat number
    is_bot: bool
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hand: list[Card] = field(default_factory=list)

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
        }

    def to_full_dict(self) -> dict:
        """Return *internal* representation, including the concealed hand."""
        return {
            "id": self.id,
            "is_bot": self.is_bot,
            "player_index": self.player_index,
            "hand": [c.to_dict() for c in self.hand],
            "hand_count": len(self.hand),
        }
