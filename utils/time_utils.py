from datetime import datetime
from zoneinfo import ZoneInfo

def get_fetched_at() -> str:
    """
    Return current time in America/New_York timezone,
    formatted as 'YYYY-MM-DD HH:MM:SS'.

    This is used as the standardized fetched_at timestamp
    across the entire data pipeline.
    """
    return datetime.now(
        ZoneInfo("America/New_York")
    ).strftime("%Y-%m-%d %H:%M:%S")