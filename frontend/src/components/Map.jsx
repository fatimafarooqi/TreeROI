function getFeatureCoordinates(feature) {
  const geometry = feature?.geometry;

  if (!geometry) {
    return [];
  }

  if (geometry.type === "Polygon") {
    return geometry.coordinates.flat(1);
  }

  if (geometry.type === "MultiPolygon") {
    return geometry.coordinates.flat(2);
  }

  return [];
}

function Map({
  mapData,
  diagnostics = [],
}) {
  const features = mapData?.features || [];

  if (!features.length) {
    return (
      <div className="map-empty">
        No map data available.
      </div>
    );
  }

  const allCoordinates = features.flatMap(
    getFeatureCoordinates
  );

  if (!allCoordinates.length) {
    return (
      <div className="map-empty">
        Map geometry unavailable.
      </div>
    );
  }

  const longitudes = allCoordinates.map(
    ([longitude]) => longitude
  );

  const latitudes = allCoordinates.map(
    ([, latitude]) => latitude
  );

  const minLon = Math.min(...longitudes);
  const maxLon = Math.max(...longitudes);
  const minLat = Math.min(...latitudes);
  const maxLat = Math.max(...latitudes);

  const width = 800;
  const height = 500;
  const padding = 20;

  const lonRange =
    maxLon - minLon || 0.001;

  const latRange =
    maxLat - minLat || 0.001;

  function project([longitude, latitude]) {
    const x =
      padding +
      ((longitude - minLon) / lonRange) *
        (width - padding * 2);

    const y =
      height -
      padding -
      ((latitude - minLat) / latRange) *
        (height - padding * 2);

    return [x, y];
  }

  function featurePath(feature) {
    const geometry = feature?.geometry;

    if (!geometry) {
      return "";
    }

    if (geometry.type === "Polygon") {
      return geometry.coordinates
        .map((ring) =>
          ring
            .map((coordinate, index) => {
              const [x, y] =
                project(coordinate);

              return `${
                index === 0 ? "M" : "L"
              } ${x} ${y}`;
            })
            .join(" ") + " Z"
        )
        .join(" ");
    }

    if (geometry.type === "MultiPolygon") {
      return geometry.coordinates
        .map((polygon) =>
          polygon
            .map((ring) =>
              ring
                .map((coordinate, index) => {
                  const [x, y] =
                    project(coordinate);

                  return `${
                    index === 0 ? "M" : "L"
                  } ${x} ${y}`;
                })
                .join(" ") + " Z"
            )
            .join(" ")
        )
        .join(" ");
    }

    return "";
  }

  // IMPORTANT:
  // Use the global JavaScript Map explicitly.
  // This component is also named "Map", so
  // "new Map()" would otherwise refer to this
  // React component.
  const diagnosticByTile =
    new globalThis.Map(
      diagnostics.map((item) => [
        String(item.tile_id),
        item,
      ])
    );

  function getTileId(feature) {
    const id =
      feature?.properties?.tile_id ??
      feature?.properties?.id ??
      feature?.id;

    return id;
  }

  function getScoreColor(score) {
    if (score == null) {
      return "#cbd5e1";
    }

    if (score >= 75) {
      return "#dc2626";
    }

    if (score >= 50) {
      return "#f97316";
    }

    if (score >= 25) {
      return "#eab308";
    }

    return "#22c55e";
  }

  return (
    <div className="map-container">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="heat-map"
      >
        {features.map((feature, index) => {
          const tileId = getTileId(feature);

          const diagnostic =
            diagnosticByTile.get(
              String(tileId)
            );

          const score =
            diagnostic?.score?.score;

          return (
            <path
              key={tileId ?? index}
              d={featurePath(feature)}
              fill={getScoreColor(score)}
              fillOpacity="0.65"
              stroke="#334155"
              strokeWidth="0.8"
            />
          );
        })}
      </svg>

      <div className="map-legend">
        <div className="legend-title">
          Intervention priority
        </div>

        <div className="legend-item">
          <span className="legend-dot critical" />
          Critical
        </div>

        <div className="legend-item">
          <span className="legend-dot high" />
          High
        </div>

        <div className="legend-item">
          <span className="legend-dot moderate" />
          Moderate
        </div>

        <div className="legend-item">
          <span className="legend-dot low" />
          Low
        </div>
      </div>
    </div>
  );
}

export default Map;
