import uuid

from thirteen_backend.utils.json import dumps, loads, ORJSONResponse


def test_dumps_and_loads_roundtrip():
    original = {
        "id": uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
        "value": 42,
        "nested": {"foo": "bar"},
    }

    dumped = dumps(original)
    assert isinstance(dumped, bytes)

    loaded = loads(dumped)
    # UUIDs should have been converted to str during serialisation
    assert loaded == {
        "id": str(original["id"]),
        "value": 42,
        "nested": {"foo": "bar"},
    }


def test_orjson_response_body_matches_dumps():
    payload = {"hello": "world"}
    resp = ORJSONResponse(content=payload)

    assert resp.body == dumps(payload)
