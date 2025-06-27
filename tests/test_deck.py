try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import types

    pytest = types.SimpleNamespace(mark=types.SimpleNamespace(asyncio=(lambda f: f)))  # type: ignore

from thirteen_backend.domain.deck import Deck, DeckConfig
from thirteen_backend.domain.player import Player


def _card_signature(card):
    """Utility to convert a Card instance to its (suit, rank) tuple."""
    return (card.suit, card.rank)


def test_deck_generation_default():
    cfg = DeckConfig()
    deck = Deck(cfg)

    assert len(deck.cards) == 52  # 1 standard deck
    # Verify uniqueness of each card in the deck
    sigs = {_card_signature(c) for c in deck.cards}
    assert len(sigs) == 52


def test_deck_multiple_decks():
    cfg = DeckConfig(deck_count=2)
    deck = Deck(cfg)

    assert len(deck.cards) == 104  # two decks

    # There *will* be duplicates across decks, but still each deck worth 52
    counts = {}
    for c in deck.cards:
        counts[_card_signature(c)] = counts.get(_card_signature(c), 0) + 1
    for count in counts.values():
        # Each unique card should appear exactly deck_count times
        assert count == 2


def test_deal_evenly_divides_cards():
    cfg = DeckConfig()
    deck = Deck(cfg)

    players = [Player(player_index=i, is_bot=False) for i in range(cfg.players_count)]
    deck.deal(players)

    cards_per_player = 52 // cfg.players_count
    assert all(len(p.hand) == cards_per_player for p in players)
    # After dealing, the deck should be empty
    assert len(deck.cards) == 0
