from typing import Any
import time as time_module

from app.services.scoring_service import (
    calculate_tile_score,
)

from app.services.environmental_service import (
    run_environmental_parameters,
)

from app.services.satellite_service import (
    run_satellite,
)

from app.services.streetview_service import (
    run_streetview,
)


# ============================================================
# BASIC EXTRACTION HELPERS
# ============================================================

def extract_temperature(
    heatmap_tile: dict[str, Any],
) -> float | None:
    """
    Extract temperature from a heatmap tile.

    Returns None when the tile does not contain
    a valid numeric temperature.
    """
    value = heatmap_tile.get("value")

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_percentage(
    segments: dict[str, Any],
    *keys: str,
) -> float | None:
    """
    Extract a segmentation percentage using
    several possible API field names.

    Returns None when no usable value exists.
    """
    for key in keys:
        value = segments.get(key)

        if value is None:
            continue

        try:
            return float(value)
        except (TypeError, ValueError):
            continue

    return None


# ============================================================
# SATELLITE DATA EXTRACTION
# ============================================================

def extract_satellite_factors(
    satellite: dict[str, Any] | None,
) -> dict[str, float | None]:
    """
    Extract scoring factors from the satellite response.
    """

    if not satellite:
        return {
            "tree_percentage": None,
            "building_percentage": None,
        }

    result = satellite.get(
        "result",
        {},
    )

    segmentation = result.get(
        "segmentation",
        {},
    )

    segments = segmentation.get(
        "segments",
        {},
    )

    return {
        "tree_percentage": extract_percentage(
            segments,
            "tree",
            "trees",
        ),

        "building_percentage": extract_percentage(
            segments,
            "building",
        ),
    }


# ============================================================
# STREETVIEW DATA EXTRACTION
# ============================================================

def extract_streetview_factors(
    streetview: dict[str, Any] | None,
) -> dict[str, float | None]:
    """
    Extract street-level tree and sky percentages
    from the Street View response.
    """

    if not streetview:
        return {
            "tree_percentage": None,
            "sky_percentage": None,
            "road_percentage": None,
            "building_percentage": None,
        }

    result = streetview.get(
        "result",
        {},
    )

    front = result.get(
        "front",
        {},
    )

    segments = front.get(
        "segments",
        {},
    )

    return {
        "tree_percentage": extract_percentage(
            segments,
            "tree",
            "trees",
        ),

        "sky_percentage": extract_percentage(
            segments,
            "sky",
        ),

        "road_percentage": extract_percentage(
            segments,
            "road",
            "road, route",
        ),

        "building_percentage": extract_percentage(
            segments,
            "building",
        ),
    }


# ============================================================
# ENVIRONMENTAL DATA EXTRACTION
# ============================================================

def extract_humidity(
    environmental: dict[str, Any] | None,
) -> float | None:
    """
    Extract relative humidity from the environmental response.
    """

    if not environmental:
        return None

    result = environmental.get(
        "result",
        {},
    )

    locations = result.get(
        "locations",
        [],
    )

    if not locations:
        return None

    location = locations[0]

    parameters = location.get(
        "parameters",
        {},
    )

    humidity = (
        parameters.get(
            "relative_humidity_percent"
        )
        or parameters.get(
            "relative_humidity"
        )
        or parameters.get(
            "humidity"
        )
    )

    if isinstance(humidity, list):
        humidity = (
            humidity[0]
            if humidity
            else None
        )

    if humidity is None:
        return None

    try:
        return float(humidity)
    except (TypeError, ValueError):
        return None


# ============================================================
# DIAGNOSIS
# ============================================================

def diagnose_tile(
    tile: dict[str, Any],
    satellite: dict[str, Any] | None,
    streetview: dict[str, Any] | None,
    environmental: dict[str, Any] | None,
    score_result: dict[str, Any],
) -> dict[str, Any]:

    diagnosis: list[str] = []
    actions: list[str] = []

    temperature = extract_temperature(
        tile
    )

    # --------------------------------------------------------
    # Satellite
    # --------------------------------------------------------

    satellite_factors = (
        extract_satellite_factors(
            satellite
        )
    )

    tree_percentage = (
        satellite_factors[
            "tree_percentage"
        ]
    )

    building_percentage = (
        satellite_factors[
            "building_percentage"
        ]
    )

    # --------------------------------------------------------
    # Temperature diagnosis
    # --------------------------------------------------------

    if temperature is not None:

        if temperature >= 39:
            diagnosis.append(
                "Very high thermal exposure."
            )

        elif temperature >= 32:
            diagnosis.append(
                "High thermal exposure."
            )

        elif temperature >= 27:
            diagnosis.append(
                "Elevated thermal exposure."
            )

    # --------------------------------------------------------
    # Satellite tree coverage
    # --------------------------------------------------------

    if tree_percentage is not None:

        if tree_percentage < 25:
            diagnosis.append(
                "Low detected tree coverage."
            )

            actions.append(
                "Prioritize tree-canopy expansion."
            )

    # --------------------------------------------------------
    # Satellite building coverage
    # --------------------------------------------------------

    if building_percentage is not None:

        if building_percentage >= 40:
            diagnosis.append(
                "High built-surface component detected."
            )

            actions.append(
                "Review shade and cooling interventions "
                "around built surfaces."
            )

    # --------------------------------------------------------
    # Street View
    # --------------------------------------------------------

    streetview_factors = (
        extract_streetview_factors(
            streetview
        )
    )

    street_tree_percentage = (
        streetview_factors[
            "tree_percentage"
        ]
    )

    sky_percentage = (
        streetview_factors[
            "sky_percentage"
        ]
    )

    road_percentage = (
        streetview_factors[
            "road_percentage"
        ]
    )

    street_building_percentage = (
        streetview_factors[
            "building_percentage"
        ]
    )

    # --------------------------------------------------------
    # Street-level tree coverage
    # --------------------------------------------------------

    if street_tree_percentage is not None:

        if street_tree_percentage < 10:
            diagnosis.append(
                "Very low visible street-level "
                "tree coverage."
            )

            actions.append(
                "Prioritize street-level tree planting "
                "and canopy expansion."
            )

    # --------------------------------------------------------
    # Street-level sky
    # --------------------------------------------------------

    if sky_percentage is not None:

        if sky_percentage >= 60:
            diagnosis.append(
                "High visible sky fraction suggests "
                "limited ground-level shade."
            )

            actions.append(
                "Review shade-structure or canopy placement."
            )

    # --------------------------------------------------------
    # Street-level road
    # --------------------------------------------------------

    if road_percentage is not None:

        if road_percentage >= 40:
            diagnosis.append(
                "High visible road-surface presence "
                "at street level."
            )

            actions.append(
                "Consider shade and heat-mitigation "
                "measures along road corridors."
            )

    # --------------------------------------------------------
    # Street-level buildings
    # --------------------------------------------------------

    if street_building_percentage is not None:

        if street_building_percentage >= 30:
            diagnosis.append(
                "Significant built-surface presence "
                "at street level."
            )

            actions.append(
                "Consider shade interventions "
                "in built-up areas."
            )

    # --------------------------------------------------------
    # Environmental diagnosis
    # --------------------------------------------------------

    humidity = extract_humidity(
        environmental
    )

    if (
        humidity is not None
        and temperature is not None
        and humidity > 60
        and temperature > 30
    ):
        diagnosis.append(
            "Hot and humid conditions increase "
            "heat-stress concern."
        )

        actions.append(
            "Review active cooling or water-based "
            "heat-relief options."
        )

    # --------------------------------------------------------
    # Data availability
    # --------------------------------------------------------

    data_status = {
        "satellite": (
            "available"
            if satellite
            else "unavailable"
        ),

        "streetview": (
            "available"
            if streetview
            else "unavailable"
        ),

        "environmental": (
            "available"
            if environmental
            else "unavailable"
        ),
    }

    return {
        "tile_id": tile.get(
            "tile_id"
        ),

        "temperature": temperature,

        "score": score_result,

        "diagnosis": diagnosis,

        "recommended_actions": list(
            dict.fromkeys(actions)
        ),

        "data_status": data_status,

        "data": {
            "satellite": satellite,
            "streetview": streetview,
            "environmental": environmental,
        },
    }


# ============================================================
# SAFE API CALL HELPERS
# ============================================================

def safe_run_satellite(
    *,
    latitude: float,
    longitude: float,
    date: str,
    start_time: str,
) -> dict[str, Any] | None:

    try:
        return run_satellite(
            latitude=latitude,
            longitude=longitude,
            date=date,
            start_time=start_time,
        )

    except Exception as exc:
        print(
            "Satellite API failed: "
            f"{type(exc).__name__}: {exc}"
        )

        return None


def safe_run_streetview(
    *,
    latitude: float,
    longitude: float,
) -> dict[str, Any] | None:

    try:
        return run_streetview(
            latitude=latitude,
            longitude=longitude,
        )

    except Exception as exc:
        print(
            "Street View API failed: "
            f"{type(exc).__name__}: {exc}"
        )

        return None


def safe_run_environmental(
    *,
    latitude: float,
    longitude: float,
    temperature: float,
    date: str,
    start_time: str,
) -> dict[str, Any] | None:

    try:
        return run_environmental_parameters(
            latitude=latitude,
            longitude=longitude,
            temperature=temperature,
            date=date,
            start_time=start_time,
        )

    except Exception as exc:
        print(
            "Environmental API failed: "
            f"{type(exc).__name__}: {exc}"
        )

        return None


# ============================================================
# TILE ENRICHMENT
# ============================================================

def enrich_tiles(
    tiles: list[dict[str, Any]],
    date: str,
    time: str,
    top_n: int,
) -> list[dict[str, Any]]:

    enriched: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # Only process requested number of tiles.
    # --------------------------------------------------------

    selected_tiles = tiles[:top_n]

    for tile in selected_tiles:

        tile_id = tile.get(
            "tile_id"
        )

        latitude = tile.get(
            "centroid_latitude"
        )

        longitude = tile.get(
            "centroid_longitude"
        )

        if latitude is None or longitude is None:

            print(
                f"\n--- Skipping tile {tile_id}: "
                "missing coordinates ---"
            )

            continue

        print(
            f"\n--- Processing tile {tile_id} ---"
        )

        # ----------------------------------------------------
        # Temperature
        # ----------------------------------------------------

        temperature = extract_temperature(
            tile
        )

        if temperature is None:

            print(
                f"Tile {tile_id}: "
                "No valid temperature value."
            )

        # ----------------------------------------------------
        # Satellite
        # ----------------------------------------------------

        start = time_module.perf_counter()

        satellite = safe_run_satellite(
            latitude=latitude,
            longitude=longitude,
            date=date,
            start_time=time,
        )

        print(
            f"Tile {tile_id}: satellite "
            f"Elapsed: "
            f"{time_module.perf_counter() - start:.2f}s"
        )

        # ----------------------------------------------------
        # Street View
        # ----------------------------------------------------

        start = time_module.perf_counter()

        streetview = safe_run_streetview(
            latitude=latitude,
            longitude=longitude,
        )

        print(
            f"Tile {tile_id}: streetview "
            f"Elapsed: "
            f"{time_module.perf_counter() - start:.2f}s"
        )

        # ----------------------------------------------------
        # Environmental
        #
        # Environmental endpoint currently requires a
        # temperature. Therefore we only call it when
        # the heatmap supplied a valid temperature.
        # ----------------------------------------------------

        environmental = None

        if temperature is not None:

            start = time_module.perf_counter()

            environmental = safe_run_environmental(
                latitude=latitude,
                longitude=longitude,
                temperature=temperature,
                date=date,
                start_time=time,
            )

            print(
                f"Tile {tile_id}: environmental "
                f"Elapsed: "
                f"{time_module.perf_counter() - start:.2f}s"
            )

        else:

            print(
                f"Tile {tile_id}: environmental "
                "Skipped because temperature is unavailable."
            )

        # ----------------------------------------------------
        # Extract scoring factors
        # ----------------------------------------------------

        satellite_factors = (
            extract_satellite_factors(
                satellite
            )
        )

        streetview_factors = (
            extract_streetview_factors(
                streetview
            )
        )

        # ----------------------------------------------------
        # Calculate TreeROI score
        #
        # NO fake temperature is inserted here.
        # ----------------------------------------------------

        score_result = calculate_tile_score(

            temperature=temperature,

            satellite_tree_percentage=(
                satellite_factors[
                    "tree_percentage"
                ]
            ),

            building_percentage=(
                satellite_factors[
                    "building_percentage"
                ]
            ),

            street_tree_percentage=(
                streetview_factors[
                    "tree_percentage"
                ]
            ),

            sky_percentage=(
                streetview_factors[
                    "sky_percentage"
                ]
            ),
        )

        print(
            f"Tile {tile_id}: "
            f"TreeROI score = "
            f"{score_result.get('score')}"
        )

        # ----------------------------------------------------
        # Diagnose tile
        # ----------------------------------------------------

        diagnosis = diagnose_tile(
            tile=tile,
            satellite=satellite,
            streetview=streetview,
            environmental=environmental,
            score_result=score_result,
        )

        enriched.append(
            diagnosis
        )

    return enriched


# ============================================================
# SORTING
# ============================================================

def sort_tiles_by_score(
    tiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Sort tiles from highest TreeROI priority to lowest.

    Tiles with valid scores appear first.

    Tiles without a valid score appear last.
    """

    return sorted(
        tiles,
        key=lambda tile: (
            tile.get("score", {}).get("score")
            is not None,

            tile.get("score", {}).get("score")
            or -1,
        ),
        reverse=True,
    )


# ============================================================
# PRIORITIZED TILE OUTPUT
# ============================================================

def build_prioritized_tiles(
    sorted_diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build the API's prioritized_tiles output from
    the final TreeROI ranking.
    """

    prioritized_tiles: list[
        dict[str, Any]
    ] = []

    for diagnostic in sorted_diagnostics:

        score_result = diagnostic.get(
            "score",
            {},
        )

        prioritized_tiles.append(
            {
                "tile_id": diagnostic.get(
                    "tile_id"
                ),

                "temperature": diagnostic.get(
                    "temperature"
                ),

                "score": score_result.get(
                    "score"
                ),

                "priority": score_result.get(
                    "priority"
                ),

                "data_completeness": (
                    score_result.get(
                        "data_completeness"
                    )
                ),
            }
        )

    return prioritized_tiles


# ============================================================
# RECOMMENDATIONS
# ============================================================

def build_recommendations(
    sorted_diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Flatten tile recommendations while preserving
    TreeROI priority order.
    """

    recommendations: list[
        dict[str, Any]
    ] = []

    for diagnostic in sorted_diagnostics:

        tile_id = diagnostic.get(
            "tile_id"
        )

        actions = diagnostic.get(
            "recommended_actions",
            [],
        )

        for action in actions:

            recommendations.append(
                {
                    "tile_id": tile_id,
                    "action": action,
                }
            )

    return recommendations


# ============================================================
# MAIN ANALYSIS HELPER
# ============================================================

def build_roi_analysis(
    tiles: list[dict[str, Any]],
    date: str,
    time: str,
    top_n: int,
) -> dict[str, Any]:
    """
    Run TreeROI enrichment and produce the final
    score-based analysis structure.

    This function does NOT call Heat Intelligence.
    """

    diagnostics = enrich_tiles(
        tiles=tiles,
        date=date,
        time=time,
        top_n=top_n,
    )

    # --------------------------------------------------------
    # Sort by TreeROI score
    # --------------------------------------------------------

    diagnostics = sort_tiles_by_score(
        diagnostics
    )

    # --------------------------------------------------------
    # Build final ranked tiles
    # --------------------------------------------------------

    prioritized_tiles = (
        build_prioritized_tiles(
            diagnostics
        )
    )

    # --------------------------------------------------------
    # Build recommendations
    # --------------------------------------------------------

    recommendations = (
        build_recommendations(
            diagnostics
        )
    )

    return {
        "prioritized_tiles": prioritized_tiles,

        "diagnostics": diagnostics,

        "recommendations": recommendations,
    }
