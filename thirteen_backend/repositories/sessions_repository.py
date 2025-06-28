from datetime import datetime, timezone

from thirteen_backend.context import APIRequestContext
from thirteen_backend.domain.game import Game
from thirteen_backend.errors import Error, ErrorCode
from thirteen_backend.logger import LOGGER
from thirteen_backend.models.game_event_model import GameEventType
from thirteen_backend.models.game_player_model import GamePlayer
from thirteen_backend.models.game_session_model import GameSession, GameStatus
from thirteen_backend.models.player_model import Player
from thirteen_backend.repositories import (
    game_event_repository,
    session_state_repository,
)
from thirteen_backend.types import GameConfig


async def create_game_session(
    *, context: APIRequestContext, cfg: GameConfig
) -> dict[str, str]:
    """Create and persist a new multiplayer *Thirteen* game session.

    The high-level workflow performed by this helper is as follows:

    1. Instantiate a new :class:`~thirteen_backend.domain.game.Game` domain
    object using the provided ``cfg`` – this yields the initial game state
    as well as four :class:`~thirteen_backend.domain.player.Player` domain
    objects (one human and three bots).
    2. Persist a corresponding :class:`~thirteen_backend.models.game_session_model.GameSession`
    row to the database marking the session *in-progress*.
    3. Persist each player to the ``player`` table and link them to the game
    via the ``game_player`` join table.
    4. Cache the initial game state and initialise the per-session sequence
    counter in Redis (both behind a single pipeline).
    5. Emit an ``INIT`` :class:`~thirteen_backend.models.game_event_model.GameEvent`
    (sequence ``0``) and push it onto the Redis event buffer.
    6. Commit the SQL transaction and execute the Redis pipeline.

    Parameters
    ----------
    context:
        Request-scoped object bundling the database session and Redis client.
    cfg:
        Configuration used to initialise the :class:`~thirteen_backend.domain.game.Game`.

    Returns
    -------
    dict[str, str]
        Mapping containing the ``session_id`` (UUID string) of the newly
        created game and the ``player_id`` representing the *human* player so
        that the caller can authenticate subsequent moves.
    """
    init_game_state = Game(cfg=cfg)
    session_id = init_game_state.id
    human_player_id: str = ""
    ts = datetime.now(timezone.utc)

    game_session = GameSession(
        id=session_id,
        status=GameStatus.IN_PROGRESS,
        created_at=ts,
        started_at=ts,
        ended_at=None,
        placements=None,
    )

    context.db_session.add(game_session)

    for player in init_game_state.players:
        if player.is_bot:
            name = f"BOT_{player.player_index}"
        else:
            name = "Human"
            human_player_id = player.id

        player_model = Player(
            id=player.id,
            name=name,
            is_bot=player.is_bot,
        )
        game_player = GamePlayer(
            game_id=game_session.id,
            player_id=player_model.id,
            seat_number=player.player_index,
        )
        context.db_session.add(player_model)
        context.db_session.add(game_player)

    await context.db_session.flush()

    session_set_success = await session_state_repository.set_session_state(
        redis_client=context.redis_client,
        game_id=game_session.id,
        game_state=init_game_state,
    )

    if not session_set_success:
        LOGGER.error(
            "Failed to set session state",
            extra={"session_id": session_id},
        )
        return Error(
            user_feedback="Failed to set session state",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        )

    await session_state_repository.initialize_session_sequencer(
        redis_client=context.redis_client,
        game_id=game_session.id,
        sequencer=0,
    )

    init_game_event = await game_event_repository.create_game_event(
        context=context,
        game_id=game_session.id,
        sequence=0,
        turn=0,
        event_type=GameEventType.INIT,
        payload=init_game_state.to_full_dict(),
        ts=ts,
        flush_to_db=False,
    )

    await session_state_repository.push_session_event(
        redis_client=context.redis_client,
        game_id=game_session.id,
        event=init_game_event,
    )

    await context.db_session.commit()

    return {"session_id": session_id, "player_id": human_player_id}
