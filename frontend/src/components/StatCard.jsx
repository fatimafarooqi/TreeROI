function StatCard({ label, value, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>

      <div className="stat-value">
        {value}
      </div>

      {subtitle && (
        <div className="stat-subtitle">
          {subtitle}
        </div>
      )}
    </div>
  );
}

export default StatCard;
