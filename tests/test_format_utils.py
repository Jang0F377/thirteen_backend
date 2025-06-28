from datetime import datetime, timezone

from thirteen_backend.utils.format_utils import format_datetime, format_uuid_as_str


def test_format_uuid_as_str():
    value = "123e4567-e89b-12d3-a456-426614174000"
    assert format_uuid_as_str(value) == value
    assert format_uuid_as_str(None) is None


def test_format_datetime_handles_datetime_and_string():
    now = datetime.now(timezone.utc)
    # When provided a datetime instance, the function should return ISO string
    iso_str = format_datetime(now)
    assert iso_str == now.isoformat()

    # Passing through an existing ISO string should return it unchanged
    assert format_datetime(iso_str) == iso_str

    # None should return None
    assert format_datetime(None) is None
