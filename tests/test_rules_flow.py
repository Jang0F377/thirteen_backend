import types

import pytest

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.rules import Rules
from thirteen_backend.types import PlayType


def _make_engine(hand: list[Card], *, current_play_type: PlayType, turn_number: int = 1, last_play=None):
    """Return a stub that mimics *Game* enough for *Rules* helpers."""
    player_stub = types.SimpleNamespace(hand=hand)
    state_stub = types.SimpleNamespace(
        players_state=[player_stub],
        current_play_type=current_play_type,
        turn_number=turn_number,
        last_play=last_play,
    )
    return types.SimpleNamespace(state=state_stub)


# ---------------------------------------------------------------------------
# get_valid_plays – OPEN pile first turn (must contain 3♦)
# ---------------------------------------------------------------------------

def test_get_valid_plays_first_turn_open_includes_3d():
    hand = [Card("D", "3"), Card("C", "3"), Card("D", "7")]
    engine = _make_engine(hand, current_play_type=PlayType.OPEN, turn_number=1)
    plays = Rules(engine).get_valid_plays(player_idx=0)

    three_d = Card("D", "3")
    assert plays, "Expected at least one opening play"
    assert all(three_d in p["cards"] for p in plays)


# ---------------------------------------------------------------------------
# get_valid_plays – SINGLE pile
# ---------------------------------------------------------------------------

def test_get_valid_plays_single_returns_all_singles():
    hand = [Card("D", "5"), Card("C", "7")]  # two cards
    engine = _make_engine(
        hand,
        current_play_type=PlayType.SINGLE,
        turn_number=2,
        last_play={"cards": [Card("D", "4")], "play_type": PlayType.SINGLE},
    )
    plays = Rules(engine).get_valid_plays(0)

    # Should produce one play per card in hand
    singles = [[c] for c in hand]
    produced = [p["cards"] for p in plays]
    assert produced == singles


# ---------------------------------------------------------------------------
# _can_play logic – SEQUENCE length enforcement
# ---------------------------------------------------------------------------

def test_can_play_sequence_requires_min_length():
    rules = Rules(engine=_make_engine([], current_play_type=PlayType.SEQUENCE))

    # hand shorter than last_play sequence length → False
    short_hand = [Card("D", "3"), Card("D", "4")]
    assert not rules._can_play(
        short_hand,
        PlayType.SEQUENCE,
        last_play={"cards": [Card("D", "5"), Card("D", "6"), Card("D", "7")]},
    )

    # long enough hand → True
    long_hand = [Card("D", "3"), Card("D", "4"), Card("C", "5")]
    assert rules._can_play(
        long_hand,
        PlayType.SEQUENCE,
        last_play={"cards": [Card("D", "5"), Card("D", "6")]},
    ) 