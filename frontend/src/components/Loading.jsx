function Loading() {
  return (
    <div className="loading-container">
      <div className="loading-spinner" />

      <h3>Analyzing urban heat exposure</h3>

      <p>
        TreeROI is examining thermal exposure,
        vegetation, built surfaces, and
        street-level conditions.
      </p>

      <p className="loading-note">
        This may take a little while.
      </p>
    </div>
  );
}

export default Loading;
