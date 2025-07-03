import asyncio

from redis.asyncio import Redis

from thirteen_backend.logger import LOGGER
from thirteen_backend.domain.game import Game
from thirteen_backend.types import PlayType, Play


async def play_bots_until_human(
    *,
    redis_client: Redis,
    engine: Game,
    seq: int,
) -> int:
    LOGGER.info(
        "Handling bot play until human",
        extra={
            "seq": seq,
            "current_turn_order": engine.state.current_turn_order,
            "turn_number": engine.state.turn_number,
            "current_leader": engine.state.current_leader,
        },
    )
    # while True:
    current_seat = engine.state.current_turn_order[
        (engine.state.turn_number - 1) % engine.cfg.players_count  # -1 because turn_number is 1-indexed
    ]
    current_player = engine.players[current_seat]
    if current_player.is_bot:
        valid_plays = engine.rules.get_valid_plays(player_idx=current_seat)
        print(f"valid_plays: {valid_plays}")
        # choices = await _choose_bot_move(engine=engine, bot_idx=next_seat)
        # print(f"choices: {choices}")
    else:
        print("human", seq)
        return seq

    # asyncio.sleep(0.5)


async def _choose_bot_move(*, engine: Game, bot_idx: int) -> list[dict]:
    pass