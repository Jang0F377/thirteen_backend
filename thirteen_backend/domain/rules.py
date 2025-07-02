from thirteen_backend.logger import LOGGER
from thirteen_backend.domain.card import Card
from thirteen_backend.domain.game import Game
from thirteen_backend.types import Play, PlayType


class Rules:
    def __init__(self, engine: Game):
        self.engine = engine

    def get_valid_plays(self, player_idx: int) -> list[Play]:
        hand = self.engine.state.players_state[player_idx].hand
        play_type = self.engine.state.current_play_type
        last_play = self.engine.state.last_play
        current_play_pile = self.engine.state.current_play_pile
        print(f"hand: {hand}")
        print(f"play_type: {play_type}")
        print(f"last_play: {last_play}")
        print(f"current_play_pile: {current_play_pile}")
        self._can_play(
            hand=hand, current_play_pile=current_play_pile, current_play_type=play_type
        )
        return []

    def _can_play(
        self,
        hand: list[Card],
        current_play_pile: list[Card],
        current_play_type: PlayType,
    ) -> bool:
        if current_play_type == PlayType.OPEN:
            LOGGER.info("OPEN")
            return True
        if current_play_type == PlayType.SINGLE:
            LOGGER.info("SINGLE")
            return len(hand) >= 1
        if current_play_type == PlayType.PAIR:
            LOGGER.info("PAIR")
            return len(hand) >= 2
        if current_play_type == PlayType.TRIPLET:
            LOGGER.info("TRIPLET")
            return len(hand) >= 3
        if current_play_type == PlayType.SEQUENCE:
            LOGGER.info("SEQUENCE")
            pass
