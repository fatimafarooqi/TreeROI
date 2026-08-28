from typing import Any

from app.fortyguard_client import get_fortyguard_client
from app.utils.polling import submit_and_wait


def run_environmental_parameters(
    latitude: float,
    longitude: float,
    temperature: float,
    date: str,
    start_time: str,
) -> dict[str, Any]:

    client = get_fortyguard_client()

    result = submit_and_wait(
        client.env_params,
        client,
        "environmental parameters",
        latitude=latitude,
        longitude=longitude,
        temperature=temperature,
        date_time={
            "start_date": date,
            "start_time": start_time,
            "filter_type": 1,
        },
    )

    if result is None:
        raise RuntimeError(
            "FortyGuard environmental parameters request failed."
        )

    return result
