# TreeROI Backend

The TreeROI backend is the API and analysis engine for the TreeROI urban heat
resilience application.

It is responsible for receiving analysis requests from the frontend, obtaining
urban heat and environmental information through FortyGuard, processing the
returned data into analysis tiles, calculating TreeROI priority scores, and
returning actionable results to the dashboard.

The backend is built with **FastAPI**.

---

## Responsibilities

The backend performs the following tasks:

1. Receive a polygon-based analysis request.
2. Generate a FortyGuard heatmap for the selected area.
3. Convert heatmap GeoJSON into analysis tiles.
4. Select candidate tiles for deeper analysis.
5. Enrich selected tiles with additional FortyGuard data.
6. Calculate TreeROI scores.
7. Diagnose conditions affecting each tile.
8. Generate recommended interventions.
9. Rank tiles according to their final TreeROI scores.
10. Return the complete analysis to the frontend.

---

## Analysis Pipeline

The main analysis endpoint follows this workflow:

```text
Analysis Request
       │
       ▼
FortyGuard Heatmap
       │
       ▼
Heatmap GeoJSON
       │
       ▼
Analysis Tiles
       │
       ▼
Candidate Tile Selection
       │
       ├───────────────┐
       │               │
       ▼               ▼
  Satellite       Street View
  Segmentation    Segmentation
       │               │
       └───────┬───────┘
               │
               ▼
      Environmental Data
               │
               ▼
       TreeROI Scoring
               │
               ▼
      Tile Diagnosis
               │
               ▼
      Final Tile Ranking
               │
               ▼
       Recommendations
               │
               ▼
        API Response
```

Temperature from the heatmap is used to identify candidate tiles for deeper
analysis. The final prioritization is based on the calculated TreeROI score.

---

## Technology Stack

| Technology     | Purpose                              |
| -------------- | ------------------------------------ |
| Python         | Backend programming language         |
| FastAPI        | REST API framework                   |
| Pydantic       | Request and configuration validation |
| Requests       | HTTP communication with FortyGuard   |
| Uvicorn        | ASGI application server              |
| FortyGuard API | Urban heat and environmental data    |

---

