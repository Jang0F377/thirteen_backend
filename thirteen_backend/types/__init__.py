from pydantic import BaseModel


class GameConfig(BaseModel):
    times_shuffled: int
    deck_count: int
    players_count: int
