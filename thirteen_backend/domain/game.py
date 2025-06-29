import uuid

from thirteen_backend.domain.deck import Deck, DeckConfig
from thirteen_backend.domain.game_state import GameState
from thirteen_backend.domain.player import Bot, Human


class Game:
    """Initialises a game: players, deck, first-turn info."""

    def __init__(self, cfg: DeckConfig | None = None):
        self.id = str(uuid.uuid4())
        self.cfg = cfg or DeckConfig()
        self.players: list[Human | Bot] = [
            (
                Human(player_index=idx, is_bot=False)
                if idx == 0
                else Bot(player_index=idx, is_bot=True)
            )
            for idx in range(self.cfg.players_count)
        ]
        self.deck = Deck(self.cfg)
        self._deal_cards()
        self.current_turn_order: list[int] = self._determine_initial_turn_order()
        self.state = GameState(
            players_state=self.players,
            current_turn_order=self.current_turn_order,
            turn_number=1,
            who_has_power=self.current_turn_order[0],
            game_id=self.id,
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

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_public_dict(self) -> dict:
        """Return client-facing serialisation (bot hands masked)."""
        return {
            "id": self.id,
            "state": self.state.to_public_dict(),
        }

    def to_full_dict(self) -> dict:
        """Return internal serialisation (includes bot hands)."""
        return {
            "id": self.id,
            "state": self.state.to_full_dict(),
        }

    # ------------------------------------------------------------------
    # Reconstruction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_state_dict(cls, data: dict) -> "Game":
        """Rebuild a *Game* instance from the cached state dictionary.

        This helper bypasses the normal constructor – which shuffles a fresh
        deck and deals cards – and instead recreates the *exact* state that
        was previously serialised and cached in Redis. Only the attributes
        required by the websocket layer (namely ``players``, ``state`` and
        ``current_turn_order``) are reinstated. The deck itself is **not**
        reconstructed because it is not needed once the initial hands have
        been dealt and play has begun.
        """
        from thirteen_backend.domain.card import Card  # local import to avoid cycles

        # ------------------------------------------------------------------
        # Re-build the domain objects encoded in *data*
        # ------------------------------------------------------------------
        state = data["state"]
        players: list[Human | Bot] = []
        for player_dict in state["players_state"]:
            hand: list[Card] = [
                Card(suit=c["suit"], rank=c["rank"])
                for c in player_dict.get("hand", [])
            ]
            if not player_dict["is_bot"]:
                players.append(
                    Human(
                        player_index=player_dict["player_index"],
                        is_bot=player_dict["is_bot"],
                        id=player_dict["id"],
                        hand=hand,
                    )
                )
            else:
                players.append(
                    Bot(
                        player_index=player_dict["player_index"],
                        is_bot=player_dict["is_bot"],
                        id=player_dict["id"],
                        hand=hand,
                    )
                )

        game_state = GameState(
            players_state=players,
            current_turn_order=state["current_turn_order"],
            turn_number=state["turn_number"],
            who_has_power=state["who_has_power"],
            game_id=data["id"],
        )

        # ------------------------------------------------------------------
        # Instantiate *Game* without invoking __init__
        # ------------------------------------------------------------------
        game = cls.__new__(cls)  # type: ignore
        game.id = data["id"]
        game.cfg = DeckConfig()
        game.players = players
        game.deck = None  # deck not required post-deal
        game.current_turn_order = state["current_turn_order"]
        game.state = game_state
        return game


# To manually test
if __name__ == "__main__":
    game = Game()
    print(f"Turn order: {game.current_turn_order}")
    print(game.to_full_dict())
