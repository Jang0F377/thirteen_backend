from dataclasses import dataclass

from thirteen_backend.domain.constants import CARD_SUITS, CARD_VALUES, RANK_ORDER, SUIT_ORDER


@dataclass(slots=True, frozen=True)
class Card:
    """Represents a single card."""

    suit: str  # D / C / H / S
    rank: str  # 3, 4, ..., A, 2

    def __post_init__(self):  # validate
        if self.suit not in CARD_SUITS:
            raise ValueError(f"Unknown suit {self.suit}")
        if self.rank not in CARD_VALUES:
            raise ValueError(f"Unknown rank {self.rank}")

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------

    @property
    def suit_name(self) -> str:  # Diamonds
        return CARD_SUITS[self.suit]

    @property
    def rank_name(self) -> str:  # Jack
        return CARD_VALUES[self.rank]

    @property
    def full_name(self) -> str:  # "Jack of Diamonds"
        return f"{self.rank_name} of {self.suit_name}"

    @property
    def comparable_value(self) -> tuple[int, int]:
        """(rank_value, suit_value) – smaller is weaker."""
        rank_val = RANK_ORDER.index(self.rank) + 1  # 1-13/14
        suit_val = SUIT_ORDER.index(self.suit) + 1  # 1-4
        return (rank_val, suit_val)

    @property
    def image_code(self) -> str:
        """Maps to the SVG in /public/cards, e.g. `JD` for Jack of Diamonds."""
        if self.rank == "10":
            return f"10{self.suit}"
        return f"{self.rank[0]}{self.suit}"

    # For JSON serialisation
    def to_dict(self):
        return {
            "rank": self.rank,
            "rankString": self.rank_name,
            "suit": self.suit,
            "suitString": self.suit_name,
            "fullName": self.full_name,
            "comparableValue": self.comparable_value,
            "cardUrl": self.image_code,
        }