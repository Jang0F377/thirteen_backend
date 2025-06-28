from fastapi import APIRouter, WebSocket

from thirteen_backend.repositories.websocket_repository import serve

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)


@router.websocket("/{session_id}/{player_id}")
async def websocket_endpoint(ws: WebSocket, session_id: str, player_id: str):
    """Thin wrapper that delegates *all* session handling to the repository."""
    await serve(
        redis_client=ws.app.state.redis_client,
        ws=ws,
        session_id=session_id,
        player_id=player_id,
    )
