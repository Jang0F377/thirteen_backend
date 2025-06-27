try:
    import pytest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import types

    pytest = types.SimpleNamespace(mark=types.SimpleNamespace(asyncio=(lambda f: f)))  # type: ignore

from thirteen_backend.domain.game import Game


def test_game_initialisation_default():
    game = Game()

    # Four players
    assert len(game.players) == 4
    cards_per_player = 52 // 4
    assert all(len(p.hand) == cards_per_player for p in game.players)

    # Turn order length & uniqueness
    assert len(game.current_turn_order) == 4
    assert sorted(game.current_turn_order) == [0, 1, 2, 3]

    # The player who owns 3♦ goes first
    owner_index = next(
        idx
        for idx, p in enumerate(game.players)
        if any(c.rank == "3" and c.suit == "D" for c in p.hand)
    )
    assert game.current_turn_order[0] == owner_index

    # to_dict returns same as state.to_dict
    assert game.to_dict() == game.state.to_dict()


def test_game_serialisation_roundtrip():
    original = Game()
    state_dict = original.to_dict()

    # Build a new Game from cached state
    restored = Game.from_state_dict(state_dict)

    # Players should have same ids & hand composition
    assert [p.id for p in restored.players] == [p.id for p in original.players]
    for orig_p, rest_p in zip(original.players, restored.players):
        assert [(c.rank, c.suit) for c in rest_p.hand] == [
            (c.rank, c.suit) for c in orig_p.hand
        ]

    # Other high-level state attributes
    assert restored.state.turn_number == original.state.turn_number
    assert restored.current_turn_order == original.current_turn_order
