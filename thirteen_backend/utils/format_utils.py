from datetime import datetime


def format_uuid_as_str(uuid: str | None) -> str | None:
    return None if uuid is None else str(uuid)


def format_datetime(date: datetime | str | None) -> str | None:
    if isinstance(date, datetime):
        return date.isoformat()
    elif date:
        return date
    else:
        return None
