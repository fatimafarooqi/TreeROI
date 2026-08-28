from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.analysis import router as analysis_router
from app.routes.health import router as health_router
from app.routes.streetview import router as streetview_router


settings = get_settings()

app = FastAPI(
    title="TreeROI API",
    description=(
        "Tile-based urban heat resilience analysis "
        "powered by FortyGuard."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(streetview_router)

@app.get("/")
def root():
    return {
        "name": "TreeROI",
        "status": "running",
        "docs": "/docs",
    }

