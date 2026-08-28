from typing import Any


def polygon_centroid(
    coordinates: list[list[float]],
) -> tuple[float, float]:

    if not coordinates:
        raise ValueError("Polygon has no coordinates.")

    longitudes = [point[0] for point in coordinates]
    latitudes = [point[1] for point in coordinates]

    return (
        sum(latitudes) / len(latitudes),
        sum(longitudes) / len(longitudes),
    )

def geojson_to_tiles(
    map_data: dict[str, Any],
    stats_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:

    stats_data = stats_data or {}

    analytic_type = stats_data.get("analytic_type")
    units = stats_data.get("units")

    features = map_data.get("features", [])

    tiles: list[dict[str, Any]] = []
    for index, feature in enumerate(features):

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        tile_id = properties.get(
            "tile_id",
            index,
        )

        # FortyGuard heatmap uses average_temperature
        # rather than the generic "value" field.

        value = properties.get("value")

        if value is None:
            value = properties.get("average_temperature")

        if value is None:
            value = properties.get("temperature")

        coordinates = geometry.get(
            "coordinates",
            [],
             )

        if (
            geometry.get("type") != "Polygon"
            or not coordinates
            or not coordinates[0]
        ):
            continue

        latitude, longitude = polygon_centroid(
            coordinates[0]
        )

        
        tiles.append(
            {
                "tile_id": tile_id,
                "analytic_type": analytic_type,
                "value": value,
                "units": units,
                "average_temperature": properties.get("average_temperature"),
                "min_temperature": properties.get("min_temperature"),
                "max_temperature": properties.get("max_temperature"),
                "centroid_latitude": latitude,
                "centroid_longitude": longitude,
            }
        )

    return tiles

def sort_tiles_by_value(
    tiles: list[dict[str, Any]],
    descending: bool = True,
) -> list[dict[str, Any]]:

    valid_tiles = [
        tile
        for tile in tiles
        if tile.get("value") is not None
    ]

    return sorted(
        valid_tiles,
        key=lambda tile: float(tile["value"]),
        reverse=descending,
    )
