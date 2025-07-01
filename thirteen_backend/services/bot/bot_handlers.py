import asyncio

from redis.asyncio import Redis

from thirteen_backend.domain.game import Game


async def play_bots_until_human(
    *,
    redis_client: Redis,
    engine: Game,
    seq: int,
) -> int:
    while True:
        next_seat = engine.state.current_turn_order[
            engine.state.turn_number % engine.cfg.players_count
        ]
        next_player = engine.players[next_seat]
        if next_player.is_bot:
            choices = await _choose_bot_move(engine=engine, bot_idx=next_seat)
        else:
            return seq

        asyncio.sleep(0.5)


async def _choose_bot_move(*, engine: Game, bot_idx: int) -> list[dict]:
    pass
