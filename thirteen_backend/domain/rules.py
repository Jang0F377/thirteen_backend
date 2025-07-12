from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from thirteen_backend.domain.classify import classify
from thirteen_backend.domain.card import Card
from thirteen_backend.domain.constants import RANK_ORDER, SUIT_ORDER
from thirteen_backend.logger import LOGGER

if TYPE_CHECKING:
    from thirteen_backend.domain.game import Game

from thirteen_backend.types import Play, PlayType


class Rules:
    def __init__(self, engine: Game):
        self.engine = engine

    def get_valid_plays(self, player_idx: int) -> list[Play] | None:
        # If the player has passed during this pile they cannot play again until
        # a new lead is established (``passed_players`` list is cleared in
        # ``GameState.handle_new_lead``).  Bail out early so that callers know
        # no action is possible besides another *pass*.
        if player_idx in self.engine.state.passed_players:
            LOGGER.debug(
                "Player %s has already passed – no valid plays until new pile",
                player_idx,
            )
            return None

        hand = self.engine.state.players_state[player_idx].hand
        current_play_type = self.engine.state.current_play_type
        last_play = self.engine.state.last_play
        print(f"hand: {hand}")
        print(f"current_play_type: {current_play_type}")
        print(f"last_play: {last_play}")

        if not self._can_play(
            hand=hand,
            current_play_type=current_play_type,
            last_play=last_play,
        ):
            return None

        return self._make_valid_plays(
            hand=hand,
            current_play_type=current_play_type,
            turn_number=self.engine.state.turn_number,
            last_play=last_play,
        )

    def _make_valid_plays(
        self,
        hand: list[Card],
        current_play_type: PlayType,
        turn_number: int,
        last_play: Play | None,
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
        elif current_play_type == PlayType.SEQUENCE:
            seqs = self._determine_sequences(hand=hand)

            # … but after the first sequence has been led everyone must keep the length
            if last_play is not None:
                needed = len(last_play["cards"])
                seqs = [s for s in seqs if len(s) == needed]

            plays = [Play(cards=s, play_type=PlayType.SEQUENCE) for s in seqs]
        elif current_play_type == PlayType.DOUBLE_SEQUENCE:
            plays = [
                Play(cards=dseq, play_type=PlayType.DOUBLE_SEQUENCE)
                for dseq in self._determine_double_sequences(hand=hand)
            ]
        elif current_play_type == PlayType.QUARTET:
            plays = [
                Play(cards=quartet, play_type=PlayType.QUARTET)
                for quartet in self._determine_quartets(hand=hand)
            ]
        elif current_play_type == PlayType.OPEN:
            if turn_number == 1:
                plays = self._determine_first_turn_open(hand=hand)
            else:
                plays = self._determine_open(hand=hand)

        # ------------------------------------------------------------------
        # Filter out plays that cannot beat the previous play
        # ------------------------------------------------------------------
        if last_play is not None and current_play_type != PlayType.OPEN:
            # Determine the strength of the previous play using the same
            # helper utilised by the bot when weighing plays.  This ensures
            # that only plays *stronger* than the last trick are considered
            # legal.  We purposely keep this logic inside the *Rules* layer
            # so that it applies uniformly to both bots and (future) human
            # moves.

            prev_cls = classify(last_play["cards"]) if last_play else None
            if prev_cls is not None:
                _, prev_strength = prev_cls

                # Keep only plays whose strength outranks the previous one
                plays = [
                    play
                    for play in plays
                    if (classify(play["cards"])[1] > prev_strength)
                ]

        return plays  # filtered list

    def _determine_first_turn_open(self, hand: list[Card]) -> list[Play]:
        """Return every legal opening play that **must** contain the 3♦ card.

        According to classic Thirteen rules, the player holding the 3♦ leads
        the very first trick and their opening combo has to include that card.
        We therefore build every single, pair, triplet, quartet, sequence and
        double-sequence that
            1. is form-valid, **and**
            2. contains the 3♦ card.
        """

        # Locate the mandatory 3♦ – if the player somehow does not have it
        # (should never happen), no opening plays are possible.
        three_diamond = next((c for c in hand if c.rank == "3" and c.suit == "D"), None)
        if three_diamond is None:
            return []

        plays: list[Play] = []

        # --- Singles ----------------------------------------------------------------
        plays.append(Play(cards=[three_diamond], play_type=PlayType.SINGLE))

        # --- Pairs / Triplets / Quartets --------------------------------------------
        threes = [c for c in hand if c.rank == "3"]

        # Pairs that include 3♦ – combine it with every other 3 the player owns.
        if len(threes) >= 2:
            for other in (c for c in threes if c is not three_diamond):
                plays.append(
                    Play(cards=[three_diamond, other], play_type=PlayType.PAIR)
                )

        # Triplets that include 3♦.
        if len(threes) >= 3:
            # Find every 2-card combination among the other 3s.
            for others in combinations(
                [c for c in threes if c is not three_diamond], 2
            ):
                plays.append(
                    Play(cards=[three_diamond, *others], play_type=PlayType.TRIPLET)
                )

        # Quartet (all four 3s).
        if len(threes) == 4:
            plays.append(Play(cards=threes, play_type=PlayType.QUARTET))

        # --- Sequences & Double-sequences -------------------------------------------
        sequences = self._determine_sequences(hand=hand)
        for seq in sequences:
            if three_diamond in seq:
                plays.append(Play(cards=seq, play_type=PlayType.SEQUENCE))

        double_sequences = self._determine_double_sequences(hand=hand)
        for dseq in double_sequences:
            if three_diamond in dseq:
                plays.append(Play(cards=dseq, play_type=PlayType.DOUBLE_SEQUENCE))

        return plays

    def _determine_open(self, hand: list[Card]) -> list[Play]:
        """Return every legal play a player can lead with when the pile is OPEN."""

        plays: list[Play] = []

        # Singles / Pairs / Triplets / Quartets --------------------------------------
        plays.extend(Play(cards=[c], play_type=PlayType.SINGLE) for c in hand)
        plays.extend(
            Play(cards=pair, play_type=PlayType.PAIR)
            for pair in self._determine_pairs(hand)
        )
        plays.extend(
            Play(cards=triplet, play_type=PlayType.TRIPLET)
            for triplet in self._determine_triplets(hand)
        )
        plays.extend(
            Play(cards=quartet, play_type=PlayType.QUARTET)
            for quartet in self._determine_quartets(hand)
        )

        # Sequences / Double-sequences ----------------------------------------------
        plays.extend(
            Play(cards=seq, play_type=PlayType.SEQUENCE)
            for seq in self._determine_sequences(hand)
        )
        plays.extend(
            Play(cards=dseq, play_type=PlayType.DOUBLE_SEQUENCE)
            for dseq in self._determine_double_sequences(hand)
        )

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

    def _determine_sequences(self, hand: list[Card]) -> list[list[Card]]:
        """Return every unique **sequence** (length ≥3) available in *hand*."""

        by_rank: dict[str, list[Card]] = {}
        for c in hand:
            by_rank.setdefault(c.rank, []).append(c)

        sequences: list[list[Card]] = []
        total_ranks = len(RANK_ORDER)

        for start_idx in range(total_ranks):
            for end_idx in range(start_idx + 2, total_ranks):  # need ≥3 cards
                segment = RANK_ORDER[start_idx : end_idx + 1]
                if not all(rank in by_rank for rank in segment):
                    continue

                # Choose one card per rank – the *weakest* card (lowest suit)
                chosen_cards: list[Card] = []
                for rank in segment:
                    cards_for_rank = sorted(
                        by_rank[rank], key=lambda c: SUIT_ORDER.index(c.suit)
                    )
                    chosen_cards.append(cards_for_rank[0])

                sequences.append(chosen_cards)

        return sequences

    def _determine_double_sequences(self, hand: list[Card]) -> list[list[Card]]:
        """Return every **double sequence** (pairs of consecutive ranks, length ≥6)."""

        by_rank: dict[str, list[Card]] = {}
        for c in hand:
            by_rank.setdefault(c.rank, []).append(c)

        double_sequences: list[list[Card]] = []
        total_ranks = len(RANK_ORDER)

        for start_idx in range(total_ranks):
            for end_idx in range(start_idx + 2, total_ranks):
                segment = RANK_ORDER[start_idx : end_idx + 1]
                if len(segment) < 3:  # needs at least 3 distinct ranks → 6 cards
                    continue
                if not all(len(by_rank.get(rank, [])) >= 2 for rank in segment):
                    continue

                chosen_cards: list[Card] = []
                for rank in segment:
                    cards_for_rank = sorted(
                        by_rank[rank], key=lambda c: SUIT_ORDER.index(c.suit)
                    )
                    chosen_cards.extend(cards_for_rank[:2])  # take two weakest

                double_sequences.append(chosen_cards)

        return double_sequences

    def _determine_quartets(self, hand: list[Card]) -> list[list[Card]]:
        """Return every combination of four cards sharing the same rank."""
        by_rank: dict[str, list[Card]] = {}
        for c in hand:
            by_rank.setdefault(c.rank, []).append(c)

        quartets: list[list[Card]] = []
        for cards in by_rank.values():
            if len(cards) == 4:
                quartets.append(cards)
        return quartets

    def _can_play(
        self,
        hand: list[Card],
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
                return len(hand) >= len(last_play["cards"])
            return False
        if current_play_type == PlayType.DOUBLE_SEQUENCE:
            pass
        if current_play_type == PlayType.QUARTET:
            pass
        return False
