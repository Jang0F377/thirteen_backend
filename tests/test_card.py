try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import types

    pytest = types.SimpleNamespace(
        mark=types.SimpleNamespace(
            parametrize=lambda *a, **k: (lambda f: f),
            asyncio=(lambda f: f),
        )
    )  # type: ignore

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.constants import (
    CARD_SUITS,
    CARD_VALUES,
    RANK_ORDER,
    SUIT_ORDER,
)


def test_valid_card_properties():
    card = Card(suit="D", rank="J")

    assert card.suit == "D"
    assert card.rank == "J"
    assert card.suit_name == CARD_SUITS["D"]
    assert card.rank_name == CARD_VALUES["J"]
    assert card.full_name == f"{card.rank_name} of {card.suit_name}"
    assert card.comparable_value == (
        RANK_ORDER.index("J") + 1,
        SUIT_ORDER.index("D") + 1,
    )
    assert card.image_code == "JD"


@pytest.mark.parametrize(
    "suit,rank,expected",
    [
        ("H", "10", "10H"),  # 10 uses full value in code
        ("S", "A", "AS"),
    ],
)
def test_image_code(suit, rank, expected):
    card = Card(suit=suit, rank=rank)
    assert card.image_code == expected


@pytest.mark.parametrize(
    "suit,rank",
    [
        ("X", "3"),  # invalid suit
        ("D", "15"),  # invalid rank
    ],
)
def test_invalid_card_raises(suit, rank):
    with pytest.raises(ValueError):
        Card(suit=suit, rank=rank)
