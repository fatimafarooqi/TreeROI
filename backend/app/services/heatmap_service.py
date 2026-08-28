from typing import Any

from app.fortyguard_client import get_fortyguard_client
from app.utils.polling import submit_and_wait


def run_heatmap(
    polygon_aoi: dict[str, Any],
    date: str,
    start_time: str,
    granularity: int,
) -> dict[str, Any]:

    client = get_fortyguard_client()

    result = submit_and_wait(
        client.heatmap,
        client,
        "heatmap",
        polygon_aoi=polygon_aoi,
        date_time={
            "start_date": date,
            "start_time": start_time,
            "filter_type": 1,
        },
        granularity=granularity,
        analytic_type="tcm",
    )

    
    if result is None:
        raise RuntimeError(
            "FortyGuard heatmap request failed."
        )

    return result
