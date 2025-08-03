from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "http_request_total", "Total HTTP Requests", ["method", "path", "status"]
)


REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration",
    ["method", "path", "status"],
)

GAME_COUNT = Counter("game_count", "Total Games")

CPU_USAGE = Gauge("cpu_usage", "CPU Usage", ["game_id"])

MEMORY_USAGE = Gauge("memory_usage", "Memory Usage", ["game_id"])

WEBSOCKET_CONNECTIONS = Gauge(
    "websocket_connections",
    "Number of active WebSocket connections",
    ["session_id"],
)

WEBSOCKET_MESSAGE_COUNT = Counter(
    "websocket_message_total",
    "Total WebSocket messages sent",
    ["session_id", "direction"],
)

GAME_EVENT_COUNT = Counter(
    "game_event_total",
    "Total game events processed",
    ["event_type"],
)


# ---------------------------------------------------------------------------
# WebSocket helpers
# ---------------------------------------------------------------------------


def increment_ws_connections(session_id: str) -> None:
    """Increase the active WebSocket connection count for *session_id*."""
    WEBSOCKET_CONNECTIONS.labels(session_id=session_id).inc()


def decrement_ws_connections(session_id: str) -> None:
    """Decrease the active WebSocket connection count for *session_id*."""
    WEBSOCKET_CONNECTIONS.labels(session_id=session_id).dec()


def increment_ws_messages(session_id: str, direction: str) -> None:
    """Increment the WebSocket message counter.

    Parameters
    ----------
    session_id:
        The game/session identifier.
    direction:
        Either ``broadcast`` or ``direct`` depending on how the message was
        delivered.
    """
    WEBSOCKET_MESSAGE_COUNT.labels(session_id=session_id, direction=direction).inc()


def track_request(method: str, path: str, status: int) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status=status).inc()


def track_request_duration(
    method: str, path: str, status: int, duration: float
) -> None:
    REQUEST_DURATION.labels(method=method, path=path, status=status).observe(duration)


def increment_game_count() -> None:
    GAME_COUNT.inc()


def increment_game_event(event_type: str) -> None:
    """Increment the counter for the supplied *event_type*."""
    GAME_EVENT_COUNT.labels(event_type=event_type).inc()
