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

## Requirements

Make sure the following are installed:

- Python 3.x
- pip

A Python virtual environment is recommended.

---

## Installation

Open a terminal in the backend directory.

Create a virtual environment:

1. Windows

```powershell
python -m venv .venv
```
Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

2. Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```
Install the required packages:

```bash
pip install -r requirements.txt
```
---

## Environment Variables

The backend requires a FortyGuard API key and the URL of the frontend that is
allowed to communicate with the API.

Create a .env file in the backend directory:

```
FORTYGUARD_API_KEY=your_fortyguard_api_key
FRONTEND_URL=http://localhost:5173
```

# Local Development

For a local Vite frontend, use:

```
FRONTEND_URL=http://localhost:5173
```

# Production

For the deployed frontend, use its origin.

For example:
```
FRONTEND_URL=https://treeroidashboard.vercel.app
```
Do not add a trailing /.

The FRONTEND_URL value is used by FastAPI's CORS middleware.

---

## Running the Backend

With the virtual environment activated, start the API using:

```bash
uvicorn app.main:app --reload
```
The local API will normally be available at:

```http://127.0.0.1:8000```

The interactive FastAPI documentation is available at:

```http://127.0.0.1:8000/docs```

---

## API Endpoints

1. Health
The backend includes a health endpoint for checking whether the API is
running.

2. Analysis
The main TreeROI analysis endpoint is:

```POST /api/analysis```
It accepts:

```JSON
{
  "polygon_aoi": {
    "type": "FeatureCollection",
    "features": []
  },
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "granularity": 100,
  "top_n": 1
}
```
3. Root
The root endpoint provides basic API information:

```GET /```

---

## FortyGuard Services

The backend contains a centralized FortyGuard client and service layer.

The current analysis workflow uses the following FortyGuard capabilities:

1. Heatmap
Generates the urban temperature heatmap for the selected polygon and
analysis time.

2. Satellite Segmentation
Provides satellite-based segmentation information used to identify factors
such as tree and building coverage.

3. Street View Segmentation
Provides street-level visual segmentation information used for factors such
as tree coverage, sky exposure, roads, and buildings.

4. Environmental Parameters
Provides environmental information used as additional context for tile
diagnosis.

---

## Tile Processing

After receiving heatmap data, the backend converts the returned GeoJSON into
individual analysis tiles.

Each tile may contain information including:

- Tile ID
- Temperature
- Centroid latitude
- Centroid longitude

The backend first identifies candidate tiles using heatmap temperature.

Only the requested number of candidate tiles are then passed through the
deeper enrichment stage.

For example:

```top_n = 1```
processes one candidate tile.

```top_n = 5```
processes five candidate tiles.

---

## TreeROI Scoring

The TreeROI scoring system combines the available information for a tile.

Relevant factors can include:

- Thermal exposure
- Tree coverage
- Built-surface coverage
- Street-level tree coverage
- Sky exposure
- Street-level conditions

The resulting score is used to rank candidate tiles.

Temperature therefore helps identify candidates, but it is not itself the
final TreeROI priority score.

---

## Diagnostics and Recommendations

After scoring, the backend generates human-readable diagnostic statements.

Examples include:
```
Very high thermal exposure.
Low detected tree coverage.
High built-surface component detected.
Very low visible street-level tree coverage.
```

The backend can also generate recommended interventions, such as:
```
Prioritize tree-canopy expansion.
Prioritize street-level tree planting and canopy expansion.
Review shade and cooling interventions around built surfaces.
```
Recommendations depend on the information successfully returned by the
enrichment services.

If an individual enrichment service is unavailable, the backend can continue
processing the tile using the remaining available information.

---

## Error Handling

The backend separates the main heatmap operation from the optional enrichment
operations.

If the heatmap does not produce usable tiles, the analysis cannot continue and
returns an error.

If an enrichment service such as satellite or Street View segmentation fails,
the backend records the failure and continues processing where possible.

This allows TreeROI to produce a result even when an individual data source is
temporarily unavailable.

---

## CORS Configuration

The FastAPI application uses the configured frontend URL for CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
For local development:

```FRONTEND_URL=http://localhost:5173```
For production:

```FRONTEND_URL=https://treeroidashboard.vercel.app```
The value must match the frontend origin.

---

## Project Structure

The backend is organized into routes, services, utilities, and the
FortyGuard client:

```
backend/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   │
│   ├── routes/
│   │   ├── analysis.py
│   │   ├── health.py
│   │   └── streetview.py
│   │
│   ├── services/
│   │   ├── heatmap_service.py
│   │   ├── satellite_service.py
│   │   ├── streetview_service.py
│   │   ├── environmental_service.py
│   │   ├── roi_service.py
│   │   └── scoring_service.py
│   │
│   ├── utils/
│   │   ├── polling.py
│   │   └── conversions.py
│   │
│   └── fortyguard_client.py
│
├── requirements.txt
├── .env
└── README.md
```

