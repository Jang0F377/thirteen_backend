from fastapi import HTTPException, status

from thirteen_backend.utils import api_responses


def game_state_not_found(game_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Game state not found for session {game_id}",
    )
