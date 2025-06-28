from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from thirteen_backend.exceptions import game_state_not_found
from thirteen_backend.logger import LOGGER
from thirteen_backend.repositories.session_state_repository import (
    get_session_sequencer,
    get_session_state,
)
from thirteen_backend.services.websocket.websocket_handlers import (
    handle_pass,
    handle_ping,
    handle_play,
    handle_ready,
    handle_resync_request,
)
from thirteen_backend.services.websocket.websocket_manager import websocket_manager
from thirteen_backend.services.websocket.websocket_utils import make_state_sync


async def serve(
    *,
    redis_client: Redis,
    ws: WebSocket,
    session_id: str,
    player_id: str,
) -> None:
    """High-level entrypoint that orchestrates an individual WebSocket session.

    This helper centralises the session initialisation, message dispatch loop
    and cleanup logic so that the FastAPI *endpoint* remains a thin adapter.
    """
    # Register the connection and obtain the *per-connection* identifier that
    # the manager uses to address messages to a single socket within a session.
    conn_id = await websocket_manager.connect(session_id=session_id, ws=ws)

    # Fetch the current game state and per-session sequence counter so that we
    # can immediately bring the newly-connected client up-to-date.
    game_state = await get_session_state(redis_client=redis_client, game_id=session_id)
    seq = await get_session_sequencer(redis_client=redis_client, game_id=session_id)

    # If either the state or sequence counter is missing the session has
    # expired or never existed – close the socket and surface a 404 via HTTP.
    if game_state is None or seq is None:
        await ws.close(code=1008, reason="Game state not found")
        return game_state_not_found(session_id)

    # Send the initial *state sync* payload so the client renders the current
    # state before dispatching any user-driven events.
    await websocket_manager.send_to(
        session_id=session_id,
        conn_id=conn_id,
        message=make_state_sync(
            session_id=session_id,
            seq=seq,
            game=game_state,
        ),
    )

    # Main receive → dispatch loop. Runs until the socket is closed.
    while True:
        try:
            incoming_message: dict[str, Any] = await ws.receive_json()
            msg_type = incoming_message.get("type")

            if msg_type == "PLAY":
                await handle_play(
                    redis_client=redis_client,
                    session_id=session_id,
                    player_id=player_id,
                    msg=incoming_message,
                )
            elif msg_type == "PASS":
                await handle_pass(
                    redis_client=redis_client,
                    session_id=session_id,
                    player_id=player_id,
                )
            elif msg_type == "READY":
                await handle_ready(
                    redis_client=redis_client,
                    session_id=session_id,
                    player_id=player_id,
                )
            elif msg_type == "PING":
                await handle_ping(
                    redis_client=redis_client,
                    session_id=session_id,
                    player_id=player_id,
                )
            elif msg_type == "RESYNC_REQUEST":
                await handle_resync_request(
                    redis_client=redis_client,
                    session_id=session_id,
                    player_id=player_id,
                    conn_id=conn_id,
                )
            else:
                LOGGER.error("Invalid message type: %s", msg_type)
                await ws.close(code=1008, reason="Invalid message type")
                break
        except WebSocketDisconnect:
            websocket_manager.disconnect(session_id=session_id, ws=ws)
            break
        except (
            Exception
        ) as exc:  # pragma: no cover – safeguard against unexpected errors
            LOGGER.exception(exc, exc_info=True)
            await ws.close(code=1008, reason="Internal server error")
            break
