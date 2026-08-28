from typing import Any

from pydantic import BaseModel, Field


class PolygonGeometry(BaseModel):
    type: str = "Polygon"
    coordinates: list[list[list[float]]]


class PolygonAOI(BaseModel):
    type: str = "FeatureCollection"
    features: list[dict[str, Any]]

class AnalysisRequest(BaseModel):
    polygon_aoi: PolygonAOI

    date: str
    time: str = "14:00"

    granularity: int = Field(
        default=80,
        ge=60,
        le=100,
    )

    top_n: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    class Tile(BaseModel):
        tile_id: str | int | None = None

        value: float | None = None

        units: str | None = None

        centroid_latitude: float
        centroid_longitude: float

class AnalysisResponse(BaseModel):
    status: str
    message: str

    heatmap: dict[str, Any] | None = None
    heat_intelligence: dict[str, Any] | None = None

    prioritized_tiles: list[dict[str, Any]] = []

    diagnostics: list[dict[str, Any]] = []

    recommendations: list[dict[str, Any]] = []

class StreetViewRequest(BaseModel):
    latitude: float
    longitude: float

    vertical_angle: float = 10.0
    horizontal_angle: float = 90.0
    back_view: bool = False
