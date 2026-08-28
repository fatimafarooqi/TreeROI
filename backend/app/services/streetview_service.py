from typing import Any

from app.fortyguard_client import get_fortyguard_client
from app.utils.polling import submit_and_wait


def run_streetview(
    latitude: float,
    longitude: float,
    vertical_angle: float = 10.0,
    horizontal_angle: float = 90.0,
    back_view: bool = False,
) -> dict[str, Any]:

    client = get_fortyguard_client()

    result = submit_and_wait(
        client.streetview,
        client,
        "street view segmentation",
        latitude=latitude,
        longitude=longitude,
        vertical_angle=vertical_angle,
        horizontal_angle=horizontal_angle,
        back_view=back_view,
        skip_on_failure=False,
    )

    if result is None:
        raise RuntimeError("Street view segmentation failed")

    return result

