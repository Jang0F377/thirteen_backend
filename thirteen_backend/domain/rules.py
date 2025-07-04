from __future__ import annotations

from typing import TYPE_CHECKING

from thirteen_backend.domain.card import Card
from thirteen_backend.logger import LOGGER

if TYPE_CHECKING:
    from thirteen_backend.domain.game import Game

from thirteen_backend.types import Play, PlayType


class Rules:
    def __init__(self, engine: Game):
        self.engine = engine

    def get_valid_plays(self, player_idx: int) -> list[Play] | None:
        hand = self.engine.state.players_state[player_idx].hand
        play_type = self.engine.state.current_play_type
        last_play = self.engine.state.last_play
        current_play_pile = self.engine.state.current_play_pile
        print(f"hand: {hand}")
        print(f"play_type: {play_type}")
        print(f"last_play: {last_play}")
        print(f"current_play_pile: {current_play_pile}")

        if not self._can_play(
            hand=hand,
            current_play_pile=current_play_pile,
            current_play_type=play_type,
            last_play=last_play,
        ):
            return None
        valid_plays = []

        return valid_plays

    def _can_play(
        self,
        hand: list[Card],
        current_play_pile: list[Card],
        current_play_type: PlayType,
        last_play: Play | None,
    ) -> bool:
        if current_play_type == PlayType.OPEN:
            return True
        if current_play_type == PlayType.SINGLE:
            return len(hand) >= 1
        if current_play_type == PlayType.PAIR:
            return len(hand) >= 2
        if current_play_type == PlayType.TRIPLET:
            return len(hand) >= 3
        if current_play_type == PlayType.SEQUENCE:
            if last_play is not None:
                return len(hand) >= len(last_play.cards)
            return False
        if current_play_type == PlayType.DOUBLE_SEQUENCE:
            pass
        if current_play_type == PlayType.QUARTET:
            pass
        return False
