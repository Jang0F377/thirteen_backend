from dataclasses import dataclass, field

from thirteen_backend.domain.card import Card
from thirteen_backend.domain.player import Bot, Human
from thirteen_backend.types import Play, PlayType


@dataclass(slots=True)
class GameState:
    players_state: list[Human | Bot]
    current_turn_order: list[int]
    turn_number: int
    current_leader: int | None  # seat idx of player who is currently leading
    game_id: str
    hand_number: int = 1
    current_play_pile: list[Card] = field(default_factory=list)
    current_play_type: PlayType = PlayType.OPEN
    passed_players: list[int] = field(
        default_factory=list
    )  # seat idx of players who have passed
    placements_this_hand: list[int] = field(
        default_factory=list
    )  # seat idx of players who have finished this hand
    last_play: Play | None = None
    
    def set_last_play(self, play: Play) -> None:
        self.last_play = play
        
    def set_current_play_type(self, play_type: PlayType) -> None:
        self.current_play_type = play_type
        
    def set_current_play_pile(self, cards: list[Card]) -> None:
        self.current_play_pile.extend(cards)
        
    def increment_turn_number(self) -> None:
        self.turn_number += 1
        
    def set_current_leader(self, player_idx: int) -> None:
        self.current_leader = player_idx
        
    def add_passed_player(self, player_idx: int) -> None:
        self.passed_players.append(player_idx)
        
    def add_placement(self, player_idx: int) -> None:
        self.placements_this_hand.append(player_idx)
        
    def reset_passed_players(self) -> None:
        self.passed_players = []
        
    def reset_current_leader(self) -> None:
        self.current_leader = None
        
    def reset_placements(self) -> None:
        self.placements_this_hand = []
        
    def reset_current_play_pile(self) -> None:
        self.current_play_pile = []
        
    def reset_current_play_type(self) -> None:
        self.current_play_type = PlayType.OPEN
        
    def reset_last_play(self) -> None:
        self.last_play = None
        
    def handle_new_lead(self, player_idx: int) -> None:
        self.set_current_leader(player_idx)
        self.reset_passed_players()
        self.reset_current_play_pile()
        self.reset_current_play_type()
        return None
    
    def handle_new_hand(self) -> None:
        self.hand_number += 1
        self.reset_passed_players()
        self.reset_placements()
        self.reset_current_play_pile()
        self.reset_current_play_type()
        self.reset_last_play()
        self.reset_current_leader()
        return None

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_public_dict(self) -> dict:
        """Return representation intended for **clients** – bot hands masked."""
        return {
            "players_state": [p.to_public_dict() for p in self.players_state],
            "current_turn_order": self.current_turn_order,
            "turn_number": self.turn_number,
            "current_leader": self.current_leader,
            "game_id": self.game_id,
            "hand_number": self.hand_number,
            "current_play_pile": [c.to_dict() for c in self.current_play_pile],
            "current_play_type": self.current_play_type,
            "passed_players": self.passed_players,
            "placements_this_hand": self.placements_this_hand,
            "last_play": self.last_play,
        }

    def to_full_dict(self) -> dict:
        """Return **internal** representation – includes bot hands."""
        return {
            "players_state": [p.to_full_dict() for p in self.players_state],
            "current_turn_order": self.current_turn_order,
            "turn_number": self.turn_number,
            "current_leader": self.current_leader,
            "game_id": self.game_id,
            "hand_number": self.hand_number,
            "current_play_pile": [c.to_dict() for c in self.current_play_pile],
            "current_play_type": self.current_play_type,
            "passed_players": self.passed_players,
            "placements_this_hand": self.placements_this_hand,
            "last_play": self.last_play,
        }
