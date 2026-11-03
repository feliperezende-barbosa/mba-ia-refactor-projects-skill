from datetime import datetime, timezone


def utcnow():
    """UTC atual como datetime naive (o SQLite guarda datetimes sem timezone)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
