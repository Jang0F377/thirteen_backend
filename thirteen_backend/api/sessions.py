from fastapi import APIRouter, Request
from pydantic import BaseModel
from thirteen_backend.adapters import postgres
from thirteen_backend.context import APIRequestContext


router = APIRouter(tags=["session"])


class GameConfig(BaseModel):
    times_shuffled: int
    deck_count: int
    players_count: int


@router.post("/sessions")
async def create_game_session(
    request: Request,
    cfg: GameConfig
):
    async with postgres.get_session() as session:
        context = APIRequestContext(request=request, db_session=session)
        
        
