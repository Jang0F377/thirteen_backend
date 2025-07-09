import types

import pytest

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.rules import Rules
from thirteen_backend.types import PlayType


@pytest.fixture()
def rules():
    """Return a *Rules* instance whose engine is a simple stub.*"""

    dummy_engine = (
        types.SimpleNamespace()
    )  # Rules helper methods in this test don't use engine
    return Rules(engine=dummy_engine)


def test_determine_pairs_triplets_quartets(rules):
    hand = [
        Card("D", "Q"),
        Card("C", "Q"),
        Card("H", "Q"),
        Card("S", "Q"),
        Card("D", "7"),
    ]

    pairs = rules._determine_pairs(hand)
    assert any(len(p) == 2 and all(c.rank == "Q" for c in p) for p in pairs)

    triplets = rules._determine_triplets(hand)
    assert any(len(t) == 3 and all(c.rank == "Q" for c in t) for t in triplets)

    quartets = rules._determine_quartets(hand)
    assert quartets == [hand[:4]]  # the first four cards form the quartet


def test_determine_sequences_and_double_sequences(rules):
    # Cards for ranks 3,4,5 – two of each to allow both sequence and double sequence
    hand = [
        Card("D", "3"),
        Card("C", "3"),
        Card("D", "4"),
        Card("C", "4"),
        Card("D", "5"),
        Card("C", "5"),
    ]

    seqs = rules._determine_sequences(hand)
    # Expect one sequence 3♦ 4♦ 5♦ (the weakest suit for each rank)
    expected_seq = [Card("D", "3"), Card("D", "4"), Card("D", "5")]
    assert expected_seq in seqs

    double_seqs = rules._determine_double_sequences(hand)
    # Should contain one double-sequence of length 6
    assert any(len(ds) == 6 for ds in double_seqs)


def test_determine_first_turn_open_requires_3d(rules):
    # Hand with 3♦ and 3♣
    hand = [Card("D", "3"), Card("C", "3"), Card("D", "7")]
    plays = rules._determine_first_turn_open(hand)

    # Every play produced must contain the 3♦ card
    three_d = Card("D", "3")
    assert plays  # at least one play
    assert all(three_d in p["cards"] for p in plays)
    # And they include at least the single 3♦ play
    assert any(len(p["cards"]) == 1 and p["cards"][0] == three_d for p in plays)
