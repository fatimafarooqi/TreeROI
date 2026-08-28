const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

// --------------------------------------------------
// FRONTEND DEVELOPMENT MODE
// true  = use mock data, NO API/credits used
// false = call real backend
// --------------------------------------------------

const USE_MOCK_DATA = true;


// --------------------------------------------------
// MOCK RESPONSE
// --------------------------------------------------

function getMockAnalysis() {
  return {
    status: "completed",

    message:
      "Mock TreeROI analysis completed successfully.",

    heatmap: {
      map_data: {},
      stats_data: {},
    },

    prioritized_tiles: [
      {
        tile_id: 12,
        value: 39.1266,
        average_temperature: 39.1266,
        min_temperature: 39.1266,
        max_temperature: 39.1266,
        centroid_latitude: 32.220059,
        centroid_longitude: -110.965944,
      },
      {
        tile_id: 25,
        value: 38.4,
        average_temperature: 38.4,
        min_temperature: 38.4,
        max_temperature: 38.4,
        centroid_latitude: 32.220975,
        centroid_longitude: -110.965944,
      },
      {
        tile_id: 38,
        value: 36.8,
        average_temperature: 36.8,
        min_temperature: 36.8,
        max_temperature: 36.8,
        centroid_latitude: 32.221891,
        centroid_longitude: -110.965943,
      },
    ],

    diagnostics: [
      {
        tile_id: 12,

        temperature: 39.1266,

        score: {
          score: 78.45,
          priority: "Critical",

          normalized_factors: {
            temperature: 0.808,
            tree_deficit: 0.692,
            built_surface: 0.921,
            street_tree_deficit: 0.844,
            sky_exposure: 0.341,
            street_shade: 0.693,
          },

          weighted_contributions: {
            temperature: 32.34,
            tree_deficit: 17.30,
            built_surface: 18.41,
            street_shade: 10.40,
          },
        },

        diagnosis: [
          "Very high thermal exposure.",
          "Low detected tree coverage.",
          "High built-surface component detected.",
          "Very low visible street-level tree coverage.",
        ],

        recommended_actions: [
          "Prioritize tree-canopy expansion.",
          "Review shade and cooling interventions around built surfaces.",
          "Prioritize street-level tree planting and canopy expansion.",
        ],

        data: {
          satellite: null,
          streetview: null,
          environmental: null,
          heat_intelligence: null,
        },
      },

      {
        tile_id: 25,

        temperature: 38.4,

        score: {
          score: 71.20,
          priority: "High",

          normalized_factors: {
            temperature: 0.76,
            tree_deficit: 0.80,
            built_surface: 0.70,
            street_tree_deficit: 0.75,
            sky_exposure: 0.40,
            street_shade: 0.645,
          },

          weighted_contributions: {
            temperature: 30.40,
            tree_deficit: 20.00,
            built_surface: 14.00,
            street_shade: 9.68,
          },
        },

        diagnosis: [
          "High thermal exposure.",
          "Low detected tree coverage.",
          "High built-surface component detected.",
        ],

        recommended_actions: [
          "Prioritize tree-canopy expansion.",
          "Consider shade interventions in built-up areas.",
        ],

        data: {
          satellite: null,
          streetview: null,
          environmental: null,
          heat_intelligence: null,
        },
      },

      {
        tile_id: 38,

        temperature: 36.8,

        score: {
          score: 62.75,
          priority: "High",

          normalized_factors: {
            temperature: 0.653,
            tree_deficit: 0.70,
            built_surface: 0.60,
            street_tree_deficit: 0.65,
            sky_exposure: 0.35,
            street_shade: 0.56,
          },

          weighted_contributions: {
            temperature: 26.12,
            tree_deficit: 17.50,
            built_surface: 12.00,
            street_shade: 8.40,
          },
        },

        diagnosis: [
          "High thermal exposure.",
          "Low detected tree coverage.",
        ],

        recommended_actions: [
          "Prioritize tree-canopy expansion.",
          "Prioritize street-level tree planting and canopy expansion.",
        ],

        data: {
          satellite: null,
          streetview: null,
          environmental: null,
          heat_intelligence: null,
        },
      },
    ],

    recommendations: [
      {
        tile_id: 12,
        action: "Prioritize tree-canopy expansion.",
      },
      {
        tile_id: 12,
        action:
          "Review shade and cooling interventions around built surfaces.",
      },
      {
        tile_id: 12,
        action:
          "Prioritize street-level tree planting and canopy expansion.",
      },
      {
        tile_id: 25,
        action: "Prioritize tree-canopy expansion.",
      },
      {
        tile_id: 25,
        action:
          "Consider shade interventions in built-up areas.",
      },
      {
        tile_id: 38,
        action: "Prioritize tree-canopy expansion.",
      },
      {
        tile_id: 38,
        action:
          "Prioritize street-level tree planting and canopy expansion.",
      },
    ],
  };
}


// --------------------------------------------------
// REAL API
// --------------------------------------------------

export async function runAnalysis({
  polygonAoi,
  date,
  time,
  granularity,
  topN,
}) {

  // ----------------------------------------------
  // MOCK MODE
  // ----------------------------------------------

  if (USE_MOCK_DATA) {
    console.log("TreeROI: MOCK MODE — no API request sent.");

    return getMockAnalysis();
  }


  // ----------------------------------------------
  // REAL BACKEND REQUEST
  // ----------------------------------------------

  const requestBody = {
    polygon_aoi: polygonAoi,
    date,
    time,
    granularity,
    top_n: topN,
  };

console.log("TreeROI request body:", requestBody);

  const response = await fetch(
    `${API_BASE_URL}/api/analysis`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(requestBody),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Analysis request failed."
    );
  }

  return data;
}
