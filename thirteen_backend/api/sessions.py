from fastapi import APIRouter, Request, status
from thirteen_backend.errors import Error
from thirteen_backend.adapters import postgres
from thirteen_backend.context import APIRequestContext
from thirteen_backend.repositories import sessions_repository
from thirteen_backend.utils.api_responses import Success, success, error
from thirteen_backend.types import GameConfig


router = APIRouter(tags=["session"])


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_game_session(request: Request, cfg: GameConfig):
    async with postgres.get_session() as session:
        context = APIRequestContext(
            request=request,
            db_session=session,
            auth_context=None,
            redis_client=request.app.state.redis_client,
        )

        result = await sessions_repository.create_game_session(context=context, cfg=cfg)

        if isinstance(result, Error):
            return error(
                error=result.error_code,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=result.user_feedback,
            )

        return success(
            content=result,
            status_code=status.HTTP_201_CREATED,
        )
