from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from thirteen_backend.exceptions import game_state_not_found
from thirteen_backend.repositories.session_state_repository import (
    get_session_sequencer,
    get_session_state,
)
from thirteen_backend.services.websocket.websocket_handlers import handle_play
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import create_state_sync_event

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)


@router.websocket("/{session_id}/{player_id}")
async def websocket_endpoint(
    ws: WebSocket,
    session_id: str,
    player_id: str,
):
    conn_id = await websocket_manager.connect(session_id=session_id, ws=ws)

    game_state = await get_session_state(
        redis_client=ws.app.state.redis_client, game_id=session_id
    )
    seq = await get_session_sequencer(
        redis_client=ws.app.state.redis_client, game_id=session_id
    )

    if game_state is None or seq is None:
        await ws.close(code=1008, reason="Game state not found")
        return game_state_not_found(session_id)

    state_sync_event = create_state_sync_event(
        game_id=session_id,
        sequence=seq,
        turn=game_state.turn_number,
        game_state=game_state,
    )

    # Send initial state sync event to the client
    await websocket_manager.send_to(
        session_id=session_id,
        conn_id=conn_id,
        message=state_sync_event.to_dict(),
    )

    while True:
        try:
            incoming_message = await ws.receive_json()
            msg_type = incoming_message["type"]
            if msg_type == "PLAY":
                await handle_play(
                    redis_client=ws.app.state.redis_client,
                    session_id=session_id,
                    player_id=player_id,
                    msg=incoming_message,
                )
            elif msg_type == "PASS":
                pass
            elif msg_type == "LEAVE":
                pass
            elif msg_type == "FINISH":
                pass
            else:
                await ws.close(code=1008, reason="Invalid message type")
                return
        except WebSocketDisconnect:
            websocket_manager.disconnect(session_id=session_id, ws=ws)
            break
        except Exception as e:
            print(e)
            await ws.close(code=1008, reason="Internal server error")
            return
