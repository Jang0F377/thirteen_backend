import asyncio

from redis.asyncio import Redis

from thirteen_backend.logger import LOGGER
from thirteen_backend.domain.game import Game


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
    while True:
        next_seat = engine.state.current_turn_order[
            engine.state.turn_number % engine.cfg.players_count
        ]
        print(f"next_seat: {next_seat}")
        next_player = engine.players[next_seat]
        print(f"next_player: {next_player}")
        if next_player.is_bot:
            choices = await _choose_bot_move(engine=engine, bot_idx=next_seat)
        else:
            return seq

        asyncio.sleep(0.5)


async def _choose_bot_move(*, engine: Game, bot_idx: int) -> list[dict]:
    pass
