function RecommendationCard({
  tileId,
  action,
}) {
  return (
    <div className="recommendation-card">
      <div className="recommendation-tile">
        Tile {tileId}
      </div>

      <div className="recommendation-action">
        {action}
      </div>
    </div>
  );
}

export default RecommendationCard;
