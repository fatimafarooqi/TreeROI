from app.services.scoring_service import calculate_tile_score


def test_minimum_risk():
    result = calculate_tile_score(
        temperature=27.0,
        satellite_tree_percentage=30.0,
        building_percentage=0.0,
        street_tree_percentage=15.0,
        sky_percentage=30.0,
    )

    assert result["score"] == 0.0
    assert result["priority"] == "Low"


def test_maximum_risk():
    result = calculate_tile_score(
        temperature=42.0,
        satellite_tree_percentage=0.0,
        building_percentage=80.0,
        street_tree_percentage=0.0,
        sky_percentage=70.0,
    )

    assert result["score"] == 100.0
    assert result["priority"] == "Critical"


def test_tile_12_score():
    result = calculate_tile_score(
        temperature=39.1266,
        satellite_tree_percentage=9.24,
        building_percentage=73.66,
        street_tree_percentage=2.34,
        sky_percentage=43.64,
    )

    assert result["score"] == 78.45
    assert result["priority"] == "Critical"


def test_hotter_tile_should_score_higher():
    cooler = calculate_tile_score(
        temperature=32.0,
        satellite_tree_percentage=10.0,
        building_percentage=50.0,
        street_tree_percentage=5.0,
        sky_percentage=50.0,
    )

    hotter = calculate_tile_score(
        temperature=39.0,
        satellite_tree_percentage=10.0,
        building_percentage=50.0,
        street_tree_percentage=5.0,
        sky_percentage=50.0,
    )

    assert hotter["score"] > cooler["score"]


def test_more_trees_should_reduce_score():
    poor_trees = calculate_tile_score(
        temperature=35.0,
        satellite_tree_percentage=5.0,
        building_percentage=50.0,
        street_tree_percentage=2.0,
        sky_percentage=50.0,
    )

    good_trees = calculate_tile_score(
        temperature=35.0,
        satellite_tree_percentage=30.0,
        building_percentage=50.0,
        street_tree_percentage=15.0,
        sky_percentage=50.0,
    )

    assert good_trees["score"] < poor_trees["score"]


def test_more_buildings_should_increase_score():
    low_buildings = calculate_tile_score(
        temperature=35.0,
        satellite_tree_percentage=15.0,
        building_percentage=20.0,
        street_tree_percentage=8.0,
        sky_percentage=50.0,
    )

    high_buildings = calculate_tile_score(
        temperature=35.0,
        satellite_tree_percentage=15.0,
        building_percentage=70.0,
        street_tree_percentage=8.0,
        sky_percentage=50.0,
    )

    assert high_buildings["score"] > low_buildings["score"]


def test_more_street_trees_should_reduce_score():
    poor_street_trees = calculate_tile_score(
        temperature=35.0,
        satellite_tree_percentage=10.0,
        building_percentage=50.0,
        street_tree_percentage=0.0,
        sky_percentage=50.0,
    )

    good_street_trees = calculate_tile_score(
        temperature=35.0,
        satellite_tree_percentage=10.0,
        building_percentage=50.0,
        street_tree_percentage=15.0,
        sky_percentage=50.0,
    )

    assert good_street_trees["score"] < poor_street_trees["score"]
