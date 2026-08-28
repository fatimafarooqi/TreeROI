from fastapi import APIRouter, HTTPException

from app.models import AnalysisRequest
from app.services.heatmap_service import run_heatmap
from app.services.roi_service import enrich_tiles
from app.utils.conversions import geojson_to_tiles


router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"],
)


@router.post("")
def analyze(request: AnalysisRequest):

    try:
        # ==================================================
        # STEP 1: Generate FortyGuard heatmap
        # ==================================================

        heatmap_response = run_heatmap(
            polygon_aoi=request.polygon_aoi.model_dump(),
            date=request.date,
            start_time=request.time,
            granularity=request.granularity,
        )

        heatmap_result = heatmap_response.get(
            "result",
            {},
        )

        map_data = heatmap_result.get(
            "map_data",
            {},
        )

        stats_data = (
            heatmap_result.get("stats_data")
            or heatmap_result.get("status_data")
            or {}
        )

        # ==================================================
        # STEP 2: Convert GeoJSON → tiles
        # ==================================================

        tiles = geojson_to_tiles(
            map_data=map_data,
            stats_data=stats_data,
        )

        if not tiles:
            raise HTTPException(
                status_code=404,
                detail="No heatmap tiles were generated.",
            )

        # ==================================================
        # STEP 3: Candidate selection
        #
        # We initially use heatmap temperature only to
        # decide which tiles deserve expensive enrichment.
        #
        # IMPORTANT:
        # This is NOT the final prioritization.
        # Final prioritization happens after TreeROI scores
        # have been calculated.
        # ==================================================

        candidate_tiles = sorted(
            tiles,
            key=lambda tile: (
                tile.get("value") is not None,
                tile.get("value", float("-inf")),
            ),
            reverse=True,
        )

        candidate_tiles = candidate_tiles[
            :request.top_n
        ]

        # ==================================================
        # STEP 4: Deep diagnosis + TreeROI scoring
        # ==================================================

        diagnostics = enrich_tiles(
            tiles=candidate_tiles,
            date=request.date,
            time=request.time,
            top_n=len(candidate_tiles),
        )

        # ==================================================
        # STEP 5: Sort by FINAL TreeROI score
        # ==================================================

        diagnostics = sorted(
            diagnostics,
            key=lambda diagnostic: (
                diagnostic.get("score", {}).get(
                    "score",
                    -1,
                )
            ),
            reverse=True,
        )

        # ==================================================
        # STEP 6: Final prioritized tiles
        #
        # The diagnostic score is now the actual
        # prioritization mechanism.
        # ==================================================

        diagnostic_by_id = {
            diagnostic.get("tile_id"): diagnostic
            for diagnostic in diagnostics
        }

        prioritized_tiles = []

        for tile in candidate_tiles:

            tile_id = tile.get("tile_id")

            diagnostic = diagnostic_by_id.get(
                tile_id
            )

            if diagnostic is None:
                continue

            prioritized_tile = dict(tile)

            prioritized_tile["roi_score"] = (
                diagnostic
                .get("score", {})
                .get("score")
            )

            prioritized_tile["priority"] = (
                diagnostic
                .get("score", {})
                .get("priority")
            )

            prioritized_tiles.append(
                prioritized_tile
            )

        prioritized_tiles.sort(
            key=lambda tile: (
                tile.get("roi_score") is not None,
                tile.get("roi_score", -1),
            ),
            reverse=True,
        )

        # ==================================================
        # STEP 7: Aggregate recommendations
        # ==================================================

        recommendations = []

        for diagnostic in diagnostics:

            tile_id = diagnostic.get(
                "tile_id"
            )

            for action in diagnostic.get(
                "recommended_actions",
                [],
            ):

                recommendations.append(
                    {
                        "tile_id": tile_id,
                        "action": action,
                    }
                )

        # ==================================================
        # STEP 8: Return response
        # ==================================================

        return {
            "status": "completed",
            "message": (
                "TreeROI analysis completed successfully."
            ),
            "heatmap": {
                "map_data": map_data,
                "stats_data": stats_data,
            },
            "prioritized_tiles": prioritized_tiles,
            "diagnostics": diagnostics,
            "recommendations": recommendations,
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    
