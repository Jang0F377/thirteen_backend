import asyncio

from redis.asyncio import Redis

from thirteen_backend.domain.classify import classify
from thirteen_backend.domain.game import Game
from thirteen_backend.logger import LOGGER
from thirteen_backend.services.state_sync import persist_and_broadcast
from thirteen_backend.types import Play, PlayType


class WeightedPlay(Play):
    strength: int


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
        current_seat = engine.state.current_turn_order[
            (engine.state.turn_number - 1)
            % engine.cfg.players_count  # -1 because turn_number is 1-indexed
        ]
        current_player = engine.players[current_seat]
        if current_player.is_bot:
            bot_move = await _choose_bot_move(engine=engine, bot_idx=current_seat)
            if not bot_move:
                print("Bot decides to pass")
                engine.apply_pass(player_idx=current_seat)
                play = None
            else:
                print(f"Bot plays: {bot_move}")
                engine.apply_play(player_idx=current_seat, play=bot_move)
                play = bot_move

            seq = await persist_and_broadcast(
                redis_client=redis_client,
                session_id=engine.id,
                play=play,
                engine=engine,
            )
            print(f"next_seq: {seq}")
        else:
            print("human", seq)
            return seq

        await asyncio.sleep(0.5)


async def _choose_bot_move(*, engine: Game, bot_idx: int) -> Play:
    valid_plays = engine.rules.get_valid_plays(player_idx=bot_idx)
    if not valid_plays:
        return []

    print(f"valid_plays: {valid_plays}")
    weighted_plays = await _weigh_plays(valid_plays=valid_plays)
    if not weighted_plays:
        return []

    print(f"weighted_plays: {weighted_plays}")

    temp_best_play = weighted_plays[0]
    return temp_best_play


async def _weigh_plays(
    *,
    valid_plays: list[Play],
) -> list[WeightedPlay]:
    weighted_plays: list[WeightedPlay] = []

    for play in valid_plays:
        res = classify(play["cards"])
        if res is None:
            continue
        _ptype, strength = res
        weighted_plays.append(
            WeightedPlay(
                cards=play["cards"],
                play_type=_ptype,
                strength=strength,
            )
        )

    weighted_plays.sort(key=lambda p: p["strength"], reverse=True)
    return weighted_plays
