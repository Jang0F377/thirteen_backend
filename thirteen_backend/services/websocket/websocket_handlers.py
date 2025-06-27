from typing import Any

from redis.asyncio import Redis


async def handle_play(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
    msg: dict[str, Any],
) -> None:
    pass


async def handle_pass(
    *,
    redis_client: Redis,
    session_id: str,
    player_id: str,
) -> None:
    pass
