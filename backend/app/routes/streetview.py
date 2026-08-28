from fastapi import APIRouter, HTTPException

from app.models import StreetViewRequest
from app.services.streetview_service import run_streetview


router = APIRouter(
    prefix="/api/streetview",
    tags=["streetview"],
)
@router.post("")
def streetview(request: StreetViewRequest):

    try:
        result = run_streetview(
            latitude=request.latitude,
            longitude=request.longitude,
            vertical_angle=request.vertical_angle,
            horizontal_angle=request.horizontal_angle,
            back_view=request.back_view,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Street View imagery unavailable.",
            )

        return {
            "status": "completed",
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    
