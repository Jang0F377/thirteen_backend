try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import types

    pytest = types.SimpleNamespace(
        mark=types.SimpleNamespace(parametrize=lambda *a, **k: (lambda f: f))
    )  # type: ignore

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.classify import classify
from thirteen_backend.types import PlayType


def _make_cards(cards: list[tuple[str, str]]):
    """Helper to build list[Card] from (rank,suit) tuples."""
    return [Card(suit=s, rank=r) for r, s in cards]


@pytest.mark.parametrize(
    "cards,expected_type,expected_strength",
    [
        ([("3", "D")], PlayType.SINGLE, 0),  # absolute weakest
        ([("3", "S")], PlayType.SINGLE, 3),
        ([("2", "S")], PlayType.SINGLE, 51),  # absolute strongest
    ],
)
def test_classify_single_strength(cards, expected_type, expected_strength):
    play_type, strength = classify(_make_cards(cards))
    assert play_type == expected_type
    assert strength == expected_strength


def test_classify_pair():
    play_type, _ = classify(_make_cards([("7", "H"), ("7", "S")]))
    assert play_type == PlayType.PAIR


def test_classify_triplet():
    play_type, _ = classify(_make_cards([("Q", "D"), ("Q", "C"), ("Q", "S")]))
    assert play_type == PlayType.TRIPLET


def test_classify_quartet():
    play_type, _ = classify(
        _make_cards([("5", "D"), ("5", "C"), ("5", "H"), ("5", "S")])
    )
    assert play_type == PlayType.QUARTET


def test_classify_sequence():
    # 6-7-8 sequence with mixed suits
    play_type, _ = classify(_make_cards([("6", "D"), ("7", "C"), ("8", "S")]))
    assert play_type == PlayType.SEQUENCE


def test_classify_double_sequence():
    # 3-3,4-4,5-5 double sequence (length 6)
    play_type, _ = classify(
        _make_cards(
            [
                ("3", "D"),
                ("3", "C"),
                ("4", "D"),
                ("4", "C"),
                ("5", "D"),
                ("5", "C"),
            ]
        )
    )
    assert play_type == PlayType.DOUBLE_SEQUENCE


def test_classify_invalid_returns_none():
    """Mixed rank pair should not be classified."""
    assert classify(_make_cards([("3", "D"), ("4", "D")])) is None 