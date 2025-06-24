from thirteen_backend.api.sessions import GameConfig

from thirteen_backend.context import APIRequestContext



async def create_game_session(
    *,
    context: APIRequestContext,
    cfg: GameConfig
) -> tuple[str, str]:
    """
    Steps:
    1. Create a new game session
    2. Create game players (2/3 bots, 1 human)
    3. Init game - shuffle deck, deal hands
    4. Write initial game state into redis
    5. Return {session_id, player_id}
    """
    