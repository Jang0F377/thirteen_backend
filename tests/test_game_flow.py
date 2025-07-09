import random

import pytest

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.game import Game
from thirteen_backend.types import PlayType


@pytest.fixture()
def seeded_game():
    """Return a *Game* instance with a deterministic deck order."""
    random.seed(12345)  # deterministic order
    return Game()


def test_apply_play_updates_state(seeded_game):
    game = seeded_game
    leader_idx = game.state.current_leader  # player who must lead first
    card_to_play = game.players[leader_idx].hand[0]
    play = {"cards": [card_to_play], "play_type": PlayType.SINGLE}

    initial_turn = game.state.turn_number
    initial_hand_size = len(game.players[leader_idx].hand)

    game.apply_play(player_idx=leader_idx, play=play)

    # Card should be removed from hand
    assert len(game.players[leader_idx].hand) == initial_hand_size - 1
    assert card_to_play not in game.players[leader_idx].hand

    # State updates ----------------------------------------------------
    assert game.state.turn_number == initial_turn + 1
    assert game.state.last_play == play
    assert card_to_play in game.state.current_play_pile
    assert game.state.current_play_type == PlayType.SINGLE


def test_apply_pass_marks_passed(seeded_game):
    game = seeded_game
    # Choose a non-leader player for simplicity
    non_leader_idx = next(
        i for i in range(len(game.players)) if i != game.state.current_leader
    )

    initial_turn = game.state.turn_number

    game.apply_pass(player_idx=non_leader_idx)

    assert non_leader_idx in game.state.passed_players
    assert game.state.turn_number == initial_turn + 1


def test_game_state_serialization_roundtrip(seeded_game):
    game = seeded_game
    # Simulate a last play to exercise serialisation helpers
    play = {
        "cards": [Card("D", "3")],
        "play_type": PlayType.SINGLE,
    }
    game.state.set_last_play(play)

    public_dict = game.state.to_public_dict()
    full_dict = game.state.to_full_dict()

    # last_play must be preserved in both serialisations
    assert public_dict["last_play"]["play_type"] == PlayType.SINGLE
    assert full_dict["last_play"]["cards"][0]["suit"] == "D"

    # Round-trip rebuild ----------------------------------------------
    restored_game = Game.from_state_dict({"id": game.id, "state": full_dict})
    assert restored_game.state.last_play is not None
    restored_play = restored_game.state.last_play
    assert restored_play["play_type"] == PlayType.SINGLE
    assert restored_play["cards"][0] == Card("D", "3")


def test_game_state_handle_new_hand_and_lead(seeded_game):
    state = seeded_game.state

    # Simulate some gameplay modifications
    state.add_passed_player(1)
    state.add_to_played_pile([Card("D", "4")])
    state.set_current_play_type(PlayType.SINGLE)
    state.set_last_play({"cards": [Card("D", "4")], "play_type": PlayType.SINGLE})
    state.set_current_leader(2)
    state.add_placement(3)

    # Capture baseline
    previous_hand_number = state.hand_number

    # Start a new hand and verify resets
    state.handle_new_hand()

    assert state.hand_number == previous_hand_number + 1
    assert state.passed_players == []
    assert state.current_play_pile == []
    assert state.current_play_type == PlayType.OPEN
    assert state.last_play is None
    assert state.current_leader is None

    # Now test handle_new_lead logic
    state.add_passed_player(0)
    state.add_passed_player(1)
    state.add_passed_player(2)
    state.handle_new_lead(player_idx=3)

    assert state.current_leader == 3
    assert state.passed_players == []
    assert state.current_play_pile == []
    assert state.current_play_type == PlayType.OPEN
