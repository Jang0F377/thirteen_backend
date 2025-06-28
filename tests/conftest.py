import json as _std_json
import sys
import types

# ---------------------------------------------------------------------------
# Stub *orjson* if missing – provide dumps/loads API compatible enough for tests
# ---------------------------------------------------------------------------
if "orjson" not in sys.modules:
    orjson_stub = types.ModuleType("orjson")

    def _dumps(obj, default=None):  # type: ignore
        # Use standard library JSON for the stub
        class _Encoder(_std_json.JSONEncoder):
            def default(self, o):  # type: ignore
                if default is not None:
                    return default(o)
                return super().default(o)

        return _std_json.dumps(obj, default=default).encode()

    def _loads(data):  # type: ignore
        if isinstance(data, (bytes, bytearray)):
            data = data.decode()
        return _std_json.loads(data)

    orjson_stub.dumps = _dumps  # type: ignore
    orjson_stub.loads = _loads  # type: ignore
    sys.modules["orjson"] = orjson_stub

# ---------------------------------------------------------------------------
# Stub minimal *fastapi* surface required for importing project modules
# ---------------------------------------------------------------------------
if "fastapi" not in sys.modules:
    fastapi_stub = types.ModuleType("fastapi")

    # Stub WebSocket + disconnect exception classes
    class _WebSocket:  # pylint:disable=too-few-public-methods
        client: "types.SimpleNamespace | None" = None

        async def accept(self):
            pass

        async def send_text(self, text: str):  # noqa: D401
            pass

        async def send_json(self, data):  # noqa: D401
            pass

    class _WebSocketDisconnect(Exception):
        pass

    fastapi_stub.WebSocket = _WebSocket  # type: ignore
    fastapi_stub.WebSocketDisconnect = _WebSocketDisconnect  # type: ignore

    # Minimal APIRouter stand-in so that import time side-effects don't explode
    class _APIRouter:  # pylint:disable=too-few-public-methods
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):  # type: ignore
            def decorator(func):
                return func

            return decorator

        def post(self, *args, **kwargs):  # type: ignore
            def decorator(func):
                return func

            return decorator

        def websocket(self, *args, **kwargs):  # type: ignore
            def decorator(func):
                return func

            return decorator

    fastapi_stub.APIRouter = _APIRouter  # type: ignore

    # Expose a *status* sub-module with commonly-used constants
    status_mod = types.ModuleType("status")
    status_mod.HTTP_200_OK = 200  # type: ignore
    status_mod.HTTP_201_CREATED = 201  # type: ignore
    status_mod.HTTP_400_BAD_REQUEST = 400  # type: ignore
    status_mod.HTTP_404_NOT_FOUND = 404  # type: ignore
    fastapi_stub.status = status_mod  # type: ignore

    # Stub responses.JSONResponse used in utils.json
    responses_mod = types.ModuleType("fastapi.responses")

    class _JSONResponse:  # pylint:disable=too-few-public-methods
        media_type = "application/json"

        def __init__(self, content, status_code=200, headers=None):  # type: ignore
            self.body = (
                content
                if isinstance(content, (bytes, bytearray))
                else _std_json.dumps(content).encode()
            )
            self.status_code = status_code
            self.headers = headers or {}

        def render(self, content):  # type: ignore
            return self.body

    responses_mod.JSONResponse = _JSONResponse  # type: ignore
    sys.modules["fastapi.responses"] = responses_mod

    # Attach *responses* to main stub for `from fastapi.responses import ...`
    fastapi_stub.responses = responses_mod  # type: ignore

    sys.modules["fastapi"] = fastapi_stub

# Ensure the submodules are also discoverable (fastapi.status etc.)
if "fastapi" in sys.modules and "fastapi.status" not in sys.modules:
    sys.modules["fastapi.status"] = sys.modules["fastapi"].status

# Ensure pydantic stub
if "pydantic" not in sys.modules:
    pydantic_stub = types.ModuleType("pydantic")

    class _BaseModel:  # pylint:disable=too-few-public-methods
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

        def model_dump(self, mode="json"):
            return self.__dict__

    class _ConfigDict(dict):
        pass

    pydantic_stub.BaseModel = _BaseModel  # type: ignore
    pydantic_stub.ConfigDict = _ConfigDict  # type: ignore

    sys.modules["pydantic"] = pydantic_stub
