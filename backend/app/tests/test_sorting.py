def test_diagnostics_are_sorted_by_score():
    diagnostics = [
        {
            "tile_id": 12,
            "score": {
                "score": 70.0,
            },
        },
        {
            "tile_id": 38,
            "score": {
                "score": 84.5,
            },
        },
        {
            "tile_id": 25,
            "score": {
                "score": 76.0,
            },
        },
    ]

    sorted_diagnostics = sorted(
        diagnostics,
        key=lambda diagnostic: (
            diagnostic.get("score", {}).get(
                "score",
                -1,
            )
        ),
        reverse=True,
    )

    assert [
        diagnostic["tile_id"]
        for diagnostic in sorted_diagnostics
    ] == [38, 25, 12]
