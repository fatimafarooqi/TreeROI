import { useMemo, useState } from "react";

import SearchBox from "../components/SearchBox";
import Loading from "../components/Loading";
import Map from "../components/Map";
import StatCard from "../components/StatCard";
import RecommendationCard from "../components/RecommendationCard";

import { runAnalysis } from "../services/api";

function Dashboard() {
  const [analysis, setAnalysis] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState(null);

  async function handleAnalyze(parameters) {
    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const result =
        await runAnalysis(parameters);

      setAnalysis(result);
    } catch (err) {
      setError(
        err?.message ||
          "Unable to complete analysis."
      );
    } finally {
      setLoading(false);
    }
  }

  const diagnostics =
    analysis?.diagnostics || [];

  const recommendations =
    analysis?.recommendations || [];

  const prioritizedTiles =
    analysis?.prioritized_tiles || [];

  const averageScore = useMemo(() => {
    if (!diagnostics.length) {
      return null;
    }

    const scores = diagnostics
      .map(
        (item) =>
          item?.score?.score
      )
      .filter(
        (score) =>
          typeof score === "number"
      );

    if (!scores.length) {
      return null;
    }

    const total = scores.reduce(
      (sum, score) =>
        sum + score,
      0
    );

    return (
      total / scores.length
    ).toFixed(1);
  }, [diagnostics]);

  const highestScore = useMemo(() => {
    const scores = diagnostics
      .map((item) =>
        item?.score?.score
      )
      .filter(
        (score) =>
          typeof score === "number"
      );

    if (!scores.length) {
      return null;
    }

    return Math.max(...scores).toFixed(1);
  }, [diagnostics]);

  const criticalTiles =
    diagnostics.filter(
      (item) =>
        item?.score?.priority ===
        "Critical"
    ).length;

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <div className="brand">
            TreeROI
          </div>

          <h1>
            Urban Heat Intervention
            Intelligence
          </h1>

          <p>
            Identify high-priority areas
            for tree canopy, shade, and
            heat-mitigation interventions.
          </p>
        </div>
      </header>

      <SearchBox
        onAnalyze={handleAnalyze}
        loading={loading}
      />

      {error && (
        <div className="error-box">
          <strong>
            Analysis failed
          </strong>

          <p>{error}</p>
        </div>
      )}

      {loading && <Loading />}

      {analysis && !loading && (
        <>
          <section className="stats-grid">
            <StatCard
              label="Tiles analyzed"
              value={
                prioritizedTiles.length
              }
              subtitle="Highest-priority tiles"
            />

            <StatCard
              label="Average score"
              value={
                averageScore ?? "—"
              }
              subtitle="Across analyzed tiles"
            />

            <StatCard
              label="Highest score"
              value={
                highestScore ?? "—"
              }
              subtitle="Maximum intervention priority"
            />

            <StatCard
              label="Critical tiles"
              value={criticalTiles}
              subtitle="Score ≥ 75"
            />
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  Priority map
                </h2>

                <p>
                  Higher scores indicate
                  greater intervention
                  priority.
                </p>
              </div>
            </div>

            <Map
              mapData={
                analysis?.heatmap?.map_data
              }
              diagnostics={diagnostics}
            />
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <h2>
                  Priority tiles
                </h2>

                <p>
                  Ranked using the TreeROI
                  intervention scoring model.
                </p>
              </div>
            </div>

            <div className="tile-grid">
              {diagnostics
                .slice()
                .sort(
                  (a, b) =>
                    (b?.score?.score ?? 0) -
                    (a?.score?.score ?? 0)
                )
                .map((diagnostic) => (
                  <div
                    className="tile-card"
                    key={diagnostic.tile_id}
                  >
                    <div className="tile-card-header">
                      <span>
                        Tile{" "}
                        {diagnostic.tile_id}
                      </span>

                      <span
                        className={`priority-badge ${String(
                          diagnostic?.score
                            ?.priority ||
                            ""
                        ).toLowerCase()}`}
                      >
                        {
                          diagnostic?.score
                            ?.priority
                        }
                      </span>
                    </div>

                    <div className="tile-score">
                      {
                        diagnostic?.score
                          ?.score ?? "—"
                      }
                      <span>/100</span>
                    </div>

                    <div className="tile-temperature">
                      Temperature:{" "}
                      {
                        diagnostic.temperature ??
                        "N/A"
                      }
                      °C
                    </div>

                    <div className="tile-diagnosis">
                      {(
                        diagnostic.diagnosis ||
                        []
                      ).map(
                        (item, index) => (
                          <div
                            key={index}
                          >
                            • {item}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <h2>
                Recommended interventions
              </h2>
            </div>

            <div className="recommendations-grid">
              {recommendations.map(
                (recommendation, index) => (
                  <RecommendationCard
                    key={`${recommendation.tile_id}-${index}`}
                    tileId={
                      recommendation.tile_id
                    }
                    action={
                      recommendation.action
                    }
                  />
                )
              )}
            </div>
          </section>
        </>
      )}
    </main>
  );
}

export default Dashboard;
