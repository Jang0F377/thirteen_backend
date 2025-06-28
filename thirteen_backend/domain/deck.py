import random
from dataclasses import dataclass

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.constants import CARD_SUITS, CARD_VALUES
from thirteen_backend.domain.player import Human, Bot


@dataclass(slots=True)
class DeckConfig:
    times_shuffled: int = 5
    deck_count: int = 1
    players_count: int = 4


class Deck:
    """Utility to create and shuffle one or multiple 52-card decks."""

    def __init__(self, cfg: DeckConfig):
        self.cfg = cfg
        self.cards: list[Card] = self._generate_cards()  # unshuffled
        self.shuffle(cfg.times_shuffled)

    def _generate_cards(self) -> list[Card]:
        cards: list[Card] = []
        for _ in range(self.cfg.deck_count):
            for suit in CARD_SUITS:
                for rank in CARD_VALUES:
                    cards.append(Card(suit=suit, rank=rank))
        return cards

    def shuffle(self, times: int = 1) -> None:
        for _ in range(max(1, times)):
            random.shuffle(self.cards)

    def deal(self, players: list[Human | Bot]) -> None:
        """Evenly distribute cards to players."""
        cards_per_player = len(self.cards) // len(players)
        for _ in range(cards_per_player):
            for p in players:
                p.hand.append(self.cards.pop())
