from thirteen_backend.domain.deck import Deck, DeckConfig
from thirteen_backend.domain.game_state import GameState
from thirteen_backend.domain.player import Player


class Game:
    """Initialises a game: players, deck, first-turn info."""

    def __init__(self, cfg: DeckConfig | None = None):
        self.cfg = cfg or DeckConfig()
        self.players: list[Player] = [
            Player(idx, is_bot=idx != 0) for idx in range(self.cfg.players_count)
        ]
        self.deck = Deck(self.cfg)
        self._deal_cards()
        self.current_turn_order: list[int] = self._determine_initial_turn_order()
        self.state = GameState(
            players_state=self.players,
            current_turn_order=self.current_turn_order,
            turn_number=1,
            who_has_power=self.current_turn_order[0],
        )

    def _deal_cards(self) -> None:
        self.deck.deal(self.players)
        # sort each hand for UX purposes
        for p in self.players:
            p.hand.sort(key=lambda c: (c.comparable_value[0], c.comparable_value[1]))

    def _determine_initial_turn_order(self) -> list[int]:
        """Player who has 3♢ goes first; order proceeds clockwise."""
        three_d_owner = next(
            idx
            for idx, pl in enumerate(self.players)
            if any(c.rank == "3" and c.suit == "D" for c in pl.hand)
        )
        order = [
            (three_d_owner + i) % self.cfg.players_count
            for i in range(self.cfg.players_count)
        ]
        return order

    def to_dict(self):
        return self.state.to_dict()


# To manually test
if __name__ == "__main__":
    game = Game()
    print(f"Turn order: {game.current_turn_order}")
    print(game.to_dict())
