from datetime import datetime, timezone
from uuid import uuid4
from thirteen_backend.errors import Error, ErrorCode
from thirteen_backend.context import APIRequestContext
from thirteen_backend.domain.game import Game
from thirteen_backend.models.game_event_model import GameEventType
from thirteen_backend.models.game_player_model import GamePlayer
from thirteen_backend.models.player_model import Player
from thirteen_backend.models.game_session_model import GameSession, GameStatus
from thirteen_backend.repositories import (
    game_event_repository,
    session_state_repository,
)
from thirteen_backend.types import GameConfig


async def create_game_session(
    *, context: APIRequestContext, cfg: GameConfig
) -> dict[str, str]:
    """
    Steps:
    1. Create a new game
    2. Initialize a new GameSession class
    3. Create initial game events
    4. Write initial game state into redis
    5. Return {session_id, player_id}
    """
    pipe = context.redis_client.pipeline()
    init_game_state = Game(cfg=cfg)

    session_id = uuid4()
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
        if player.player_index == 0:
            name = "Human"
            is_bot = False
            human_player_id = player.id
        else:
            name = f"BOT_{player.player_index}"
            is_bot = True

        player_model = Player(
            id=player.id,
            name=name,
            is_bot=is_bot,
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
        pipe=pipe,
        game_id=game_session.id,
        game_state=init_game_state,
    )

    if not session_set_success:
        return Error(
            user_feedback="Failed to set session state",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        )
        
    await session_state_repository.initialize_session_sequencer(
        pipe=pipe,
        game_id=game_session.id,
        sequencer=0,
    )

    init_game_event = await game_event_repository.create_game_event(
        context=context,
        game_id=game_session.id,
        sequence=0,
        turn=0,
        event_type=GameEventType.INIT,
        payload=init_game_state.to_dict(),
        ts=ts,
        flush_to_db=False,
    )

    await session_state_repository.push_session_event(
        pipe=pipe,
        game_id=game_session.id,
        event=init_game_event,
    )

    await pipe.execute()
    await context.db_session.commit()
    

    return {"session_id": session_id, "player_id": human_player_id}
