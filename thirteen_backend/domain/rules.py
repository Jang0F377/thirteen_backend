from __future__ import annotations

from itertools import combinations
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

        return self._make_valid_plays(hand=hand, current_play_type=play_type)

    def _make_valid_plays(
        self, hand: list[Card], current_play_type: PlayType
    ) -> list[Play]:
        plays = []
        if current_play_type == PlayType.SINGLE:
            plays = [Play(cards=[c], play_type=PlayType.SINGLE) for c in hand]
        elif current_play_type == PlayType.PAIR:
            plays = [
                Play(cards=pair, play_type=PlayType.PAIR)
                for pair in self._determine_pairs(hand=hand)
            ]
        elif current_play_type == PlayType.TRIPLET:
            plays = [
                Play(cards=triplet, play_type=PlayType.TRIPLET)
                for triplet in self._determine_triplets(hand=hand)
            ]
        elif current_play_type == PlayType.OPEN:
            plays = self._determine_open(hand=hand)

        return plays
    
    def _determine_open(self, hand: list[Card]) -> list[Play]:
        plays = []
        singles = [Play(cards=[c], play_type=PlayType.SINGLE) for c in hand]
        pairs = [
            Play(cards=pair, play_type=PlayType.PAIR)
            for pair in self._determine_pairs(hand=hand)
        ]
        triplets = [
            Play(cards=triplet, play_type=PlayType.TRIPLET)
            for triplet in self._determine_triplets(hand=hand)
        ]
        plays.extend(singles)
        plays.extend(pairs)
        plays.extend(triplets)
        return plays

    def _determine_triplets(self, hand: list[Card]) -> list[list[Card]]:
        """Return every unique combination of 3 cards sharing the same rank."""
        by_rank: dict[str, list[Card]] = {}
        for c in hand:
            by_rank.setdefault(c.rank, []).append(c)

        triplets: list[list[Card]] = []
        for cards in by_rank.values():
            if len(cards) >= 3:
                for combo in combinations(cards, 3):
                    triplets.append(list(combo))
        return triplets

    def _determine_pairs(self, hand: list[Card]) -> list[list[Card]]:
        """Return every unique combination of 2 cards sharing the same rank."""
        by_rank: dict[str, list[Card]] = {}
        for c in hand:
            by_rank.setdefault(c.rank, []).append(c)

        pairs: list[list[Card]] = []
        for cards in by_rank.values():
            if len(cards) >= 2:
                for combo in combinations(cards, 2):
                    pairs.append(list(combo))
        return pairs

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
