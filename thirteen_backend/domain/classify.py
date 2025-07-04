from thirteen_backend.domain.card import Card
from thirteen_backend.domain.constants import RANK_ORDER, SUIT_ORDER
from thirteen_backend.types import PlayType


def _card_strength(card: Card) -> int:
    """
    Return a single sortable integer that expresses the 'power' of a card.

    Why `rank_val * 4 + suit_val`?
        1.  There are **4 suits**.  Multiplying the zero-based rank index
            by 4 reserves a contiguous block of four numbers for every rank
            (3 = 0-3, 4 = 4-7, …, 2 = 48-51).
        2.  Adding the zero-based suit index then orders the cards **within
            that rank block** from weakest to strongest, following the
            Vietnamese hierarchy ♦ < ♣ < ♥ < ♠.

    This yields a perfect linear order where:
        3♦ → 0   (absolute weakest)
        3♠ → 3
        4♦ → 4
        …
        2♠ → 51  (absolute strongest)

    Having a scalar instead of a `(rank, suit)` tuple lets the rest of the
    engine compare and sort cards with ordinary integer operators – simple
    and fast.
    """
    rank_val = RANK_ORDER.index(card.rank)  # 0-based rank (3 → 0 … 2 → 12)
    suit_val = SUIT_ORDER.index(card.suit)  # 0-based suit (♦ → 0 … ♠ → 3)
    return rank_val * 4 + suit_val


def _classify_single(cards: list[Card]) -> tuple[PlayType, int] | None:
    if len(cards) == 1:
        return PlayType.SINGLE, _card_strength(cards[0])
    return None


def _classify_pair(cards: list[Card]) -> tuple[PlayType, int] | None:
    if len(cards) == 2 and cards[0].rank == cards[1].rank:
        return PlayType.PAIR, max(_card_strength(c) for c in cards)
    return None


def _classify_triplet(cards: list[Card]) -> tuple[PlayType, int] | None:
    if len(cards) == 3 and len({c.rank for c in cards}) == 1:
        return PlayType.TRIPLET, max(_card_strength(c) for c in cards)
    return None


def _classify_quartet(cards: list[Card]) -> tuple[PlayType, int] | None:
    if len(cards) == 4 and len({c.rank for c in cards}) == 1:
        return PlayType.QUARTET, max(_card_strength(c) for c in cards)
    return None


def _classify_sequence(cards: list[Card]) -> tuple[PlayType, int] | None:
    if len(cards) < 3:
        return None

    by_rank = sorted(cards, key=lambda c: RANK_ORDER.index(c.rank))
    ranks = [c.rank for c in by_rank]
    idxs = [RANK_ORDER.index(r) for r in ranks]
    if all(b - a == 1 for a, b in zip(idxs, idxs[1:])):
        return PlayType.SEQUENCE, max(_card_strength(c) for c in by_rank)
    return None


def _classify_double_sequence(cards: list[Card]) -> tuple[PlayType, int] | None:
    if len(cards) < 6 or len(cards) % 2 != 0:
        return None

    by_rank: dict[str, list[Card]] = {}
    for c in cards:
        by_rank.setdefault(c.rank, []).append(c)

    if any(len(v) != 2 for v in by_rank.values()):
        return None

    sorted_ranks = sorted(by_rank.keys(), key=RANK_ORDER.index)
    idxs = [RANK_ORDER.index(r) for r in sorted_ranks]
    if all(b - a == 1 for a, b in zip(idxs, idxs[1:])):
        flat_cards = [c for pair in sorted_ranks for c in by_rank[pair]]
        return PlayType.DOUBLE_SEQUENCE, max(_card_strength(c) for c in flat_cards)
    return None


_CLASSIFIERS = (
    _classify_single,
    _classify_pair,
    _classify_triplet,
    _classify_quartet,
    _classify_double_sequence,  # must be before _classify_sequence
    _classify_sequence,
)


def classify(cards: list[Card]) -> tuple[PlayType, int] | None:
    for classifier in _CLASSIFIERS:
        result = classifier(cards)
        if result is not None:
            return result
    return None
