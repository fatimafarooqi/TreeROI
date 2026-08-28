from typing import Any

from app.fortyguard_client import get_fortyguard_client
from app.utils.polling import submit_and_wait


def run_satellite(
    latitude: float,
    longitude: float,
    date: str,
    start_time: str,
    granularity: int = 80,
) -> dict[str, Any]:
    client = get_fortyguard_client()

    result = submit_and_wait(
        client.satellite,
        client,
        "satellite segmentation",
        sat={
            "latitude": latitude,
            "longitude": longitude,
        },
        date_time={
            "start_date": date,
            "start_time": start_time,
            "filter_type": 1,
        },
        granularity=granularity,
    )

    if result is None:
        raise RuntimeError(
            "FortyGuard satellite request failed."
        )

    return result
