import uuid

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.deck import Deck, DeckConfig
from thirteen_backend.domain.game_state import GameState
from thirteen_backend.domain.player import Bot, Human
from thirteen_backend.domain.rules import Rules
from thirteen_backend.logger import LOGGER
from thirteen_backend.types import Play, PlayType


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
            current_leader=self.current_turn_order[0],
            game_id=self.id,
        )
        self.rules = Rules(engine=self)

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

    def _pop_cards_from_hand(self, player_idx: int, cards: list[Card]) -> None:
        hand = self.players[player_idx].hand
        for card in cards:
            try:
                hand.remove(card)
            except ValueError as exc:
                raise ValueError(
                    f"Card {card} not found in player {player_idx}'s hand"
                ) from exc

    def apply_pass(self, player_idx: int) -> None:
        LOGGER.info("Applying pass for player %s", player_idx)
        if player_idx not in self.state.passed_players:
            self.state.add_passed_player(player_idx)
        if self.state.has_all_passed():
            self.state.handle_new_lead(player_idx=self.state.get_new_leader_idx())
        self.state.increment_turn_number()
        self._handle_player_gone_out(player_idx=player_idx)

    def apply_play(self, player_idx: int, play: Play) -> None:
        LOGGER.info("Applying play for player %s: %s", player_idx, play["cards"])
        self._pop_cards_from_hand(player_idx=player_idx, cards=play["cards"])
        if self.state.current_leader is None:
            self.state.set_current_leader(player_idx)
        if self.state.current_play_type == PlayType.OPEN:
            self.state.set_current_play_type(play["play_type"])

        self.state.add_to_played_pile(play["cards"])
        self.state.set_last_play(play)
        self.state.increment_turn_number()
        self._handle_player_gone_out(player_idx=player_idx)

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

    # --------------------------------------------------------------
    #  Hand-completion helpers
    # --------------------------------------------------------------
    def _handle_player_gone_out(self, player_idx: int) -> None:
        """
        Triggered whenever a player's hand might have reached zero cards.
        If this is the first time we see that player at 0 cards during the
        current hand we…
        1.  append their seat index to state.placements_this_hand
        2.  write the resulting *rank* (1st, 2nd …) into the player's own
            `placements` list so it survives between hands
        3.  optionally remove the seat from `current_turn_order`
        """
        if (
            len(self.players[player_idx].hand) > 0
            or player_idx in self.state.placements_this_hand
        ):
            return  # nothing to do

        LOGGER.info("Handling player %s going out", player_idx)
        self.state.add_placement(player_idx)  # 1
        rank = len(self.state.placements_this_hand)
        self.players[player_idx].placements.append(rank)  # 2

        # 3 – keeps the turn-rotation code simple because we will no longer
        #     land on a seat that cannot act.
        self.state.remove_player_from_turn_order(player_idx)

        # If only one active player remains the hand is over
        if len(self.state.current_turn_order) == 1:
            last_idx = self.state.current_turn_order[0]
            self.state.add_placement(last_idx)
            self.players[last_idx].placements.append(
                len(self.state.placements_this_hand)
            )
            LOGGER.info(
                "This game has ended - there is only one player with cards left",
                extra={
                    "game_id": self.id,
                    "placements": self.state.placements_this_hand,
                    "game_state": self.state.to_full_dict(),
                },
            )
            self._start_new_hand()
        # else:
        # pass  # TODO: handle player going out in the middle of a hand

    def _start_new_hand(self) -> None:
        LOGGER.info("Starting a new hand", extra={"game_id": self.id})
        self.state.handle_new_hand()
        self.deck = Deck(self.cfg)
        self._deal_cards()
        self.current_turn_order = self._determine_initial_turn_order()
        self.state.current_turn_order = self.current_turn_order
        self.state.current_leader = self.current_turn_order[0]

    # ------------------------------------------------------------------
    # Reconstruction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_state_dict(cls, data: dict) -> "Game":
        """Rebuild a *Game* instance from the cached state dictionary.

        This helper bypasses the normal constructor and instead recreates
        the *exact* state that was previously serialised and cached in Redis.
        Only the attributes required by the websocket layer (namely
        ``players``, ``state`` and ``current_turn_order``) are reinstated.
        The deck itself is **not** reconstructed because it is not needed
        once the initial hands have been dealt and play has begun.
        """
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
            current_leader=state["current_leader"],
            hand_number=state["hand_number"],
            current_play_pile=[
                Card(suit=c["suit"], rank=c["rank"]) for c in state["current_play_pile"]
            ],
            current_play_type=state["current_play_type"],
            passed_players=state["passed_players"],
            placements_this_hand=state["placements_this_hand"],
            last_play=(
                {
                    "cards": [
                        Card(suit=c["suit"], rank=c["rank"])
                        for c in state["last_play"]["cards"]
                    ],
                    "play_type": state["last_play"]["play_type"],
                }
                if state.get("last_play")
                else None
            ),
            game_id=data["id"],
        )

        # ------------------------------------------------------------------
        # Instantiate *Game* without invoking __init__
        # ------------------------------------------------------------------
        game = cls.__new__(cls)
        game.id = data["id"]
        game.cfg = DeckConfig()
        game.players = players
        game.deck = None  # deck not required post-deal
        game.current_turn_order = state["current_turn_order"]
        game.state = game_state
        game.rules = Rules(engine=game)
        return game


# To manually test
if __name__ == "__main__":
    game = Game()
    print(f"Turn order: {game.current_turn_order}")
    print(game.to_full_dict())
