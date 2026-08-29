 # TreeROI — Where Should We Plant Trees?

TreeROI is a tile-based urban heat resilience application that helps identify
locations where tree planting and other cooling interventions may have the
greatest potential benefit.

Instead of looking at temperature alone, TreeROI combines urban heat data with
additional environmental and visual information to produce a TreeROI priority
score for selected locations.

The goal is to transform raw urban climate data into a practical
decision-support tool for municipalities, urban planners, and climate
resilience teams.

---

## How TreeROI Works

A user selects an area of interest by drawing a polygon on the map and provides
the analysis date, time, heatmap granularity, and number of tiles to prioritize.

The application then follows this pipeline:

    User
      │
      ▼
    Draw polygon on map
      │
      ▼
    TreeROI Frontend
      │
      │  polygon + date + time + granularity + top N
      ▼
    TreeROI Backend
      │
      ▼
    FortyGuard Heatmap
      │
      ▼
    Heatmap converted into analysis tiles
      │
      ▼
    Candidate tiles selected
      │
      ├──────────────► FortyGuard Satellite Segmentation
      │
      ├──────────────► FortyGuard Street View Segmentation
      │
      └──────────────► FortyGuard Environmental Parameters
      │
      ▼
    TreeROI scoring
      │
      ▼
    Tile diagnosis
      │
      ▼
    Prioritized locations + recommendations
      │
      ▼
    TreeROI Dashboard

### 1. Area Selection

The user draws a polygon around the urban area they want to analyze.

TreeROI currently focuses on polygon-based area selection.

### 2. Heatmap Generation

The polygon is sent to the backend, which requests a FortyGuard heatmap
for the selected location, date, time, and granularity.

The returned heatmap is converted into individual analysis tiles.

Each tile contains information such as its location and temperature.

### 3. Candidate Tile Selection

TreeROI initially uses heatmap temperature to identify candidate tiles for
deeper analysis.

The hottest candidate locations are sent through the more expensive enrichment
steps.

This temperature-based selection is only used to determine which tiles receive
deeper analysis. It is not the final TreeROI prioritization.

### 4. Multi-source Enrichment

For each selected tile, TreeROI attempts to retrieve additional information
using FortyGuard services.

These include:

- Satellite segmentation
- Street View segmentation
- Environmental parameters

The application extracts relevant factors such as:

- Temperature
- Tree coverage
- Building/built-surface coverage
- Street-level tree coverage
- Visible sky
- Road presence
- Environmental conditions

### 5. TreeROI Score

The extracted information is passed to the TreeROI scoring system.

The scoring system produces a priority score and priority category for each
analyzed tile.

The final ranking is based on the TreeROI score rather than temperature alone.

### 6. Diagnosis and Recommendations

TreeROI converts the available data into human-readable findings.

Examples include:

- High thermal exposure
- Low detected tree coverage
- High built-surface component
- Very low visible street-level tree coverage
- High visible road-surface presence

Based on the detected conditions, TreeROI can recommend interventions such as:

- Tree-canopy expansion
- Street-level tree planting
- Shade interventions
- Cooling interventions around built surfaces
- Heat-mitigation measures along road corridors

Recommendations are generated from the data that is successfully available for
the tile.

If sufficient information is not available to identify a specific intervention,
the dashboard reports that no specific intervention was identified from the
available data.

---

## Dashboard Output

After analysis, the TreeROI dashboard presents:

- Selected analysis area
- Heatmap information
- Prioritized tiles
- TreeROI scores
- Priority categories
- Tile diagnostics
- Recommended interventions
- Data availability for the different enrichment sources

The result is intended to make the analysis understandable to a
decision-maker rather than requiring them to interpret raw API responses.

---

## FortyGuard Integration

TreeROI uses FortyGuard services as the data and analysis layer for its urban
heat intelligence workflow.

The backend integrates with FortyGuard for:

- Heatmap generation
- Satellite segmentation
- Street View segmentation
- Environmental parameters

The application also contains support for FortyGuard's Heat Intelligence
endpoint in the API client, although the current TreeROI analysis pipeline
does not depend on Heat Intelligence for its final scoring.

---

## Technology Stack

### Frontend

- React
- Vite
- React Leaflet
- Leaflet
- Leaflet Draw

### Backend

- Python
- FastAPI
- Pydantic
- Requests

### External Data / Analysis

- FortyGuard API
- OpenStreetMap tiles through Leaflet


---

## Project Structure

```text
TreeROI/
│
├── README.md
│
├── frontend/
│   ├── README.md
│   └── ...
│
└── backend/
    ├── README.md
    └── ...
