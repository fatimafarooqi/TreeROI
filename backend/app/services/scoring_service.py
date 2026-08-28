from typing import Any


# ============================================================
# SCORE WEIGHTS
# ============================================================

TEMPERATURE_WEIGHT = 40.0
TREE_DEFICIT_WEIGHT = 25.0
BUILT_SURFACE_WEIGHT = 20.0
STREET_SHADE_WEIGHT = 15.0

TOTAL_WEIGHT = (
    TEMPERATURE_WEIGHT
    + TREE_DEFICIT_WEIGHT
    + BUILT_SURFACE_WEIGHT
    + STREET_SHADE_WEIGHT
)


# ============================================================
# NORMALIZATION LIMITS
# ============================================================

# Temperature:
# <= 27 C -> 0 risk
# >= 42 C -> maximum risk

TEMPERATURE_MIN = 27.0
TEMPERATURE_MAX = 42.0


# Satellite tree coverage:
# 0% -> maximum vegetation deficit
# 30% -> no vegetation deficit

TREE_TARGET_PERCENT = 30.0


# Satellite building coverage:
# 0% -> no built-surface exposure
# 80% -> maximum built-surface exposure

BUILDING_MAX_PERCENT = 80.0


# Street-view tree coverage:
# 0% -> maximum street-level vegetation deficit
# 15% -> no vegetation deficit

STREET_TREE_TARGET_PERCENT = 15.0


# Street-view sky:
# 30% -> low sky exposure
# 70% -> maximum sky exposure

SKY_MIN_PERCENT = 30.0
SKY_MAX_PERCENT = 70.0


# ============================================================
# GENERIC HELPERS
# ============================================================

def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """
    Keep a numeric value inside a specified range.
    """
    return max(minimum, min(value, maximum))


def normalize_range(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Normalize a value to the range 0-1.

    Values below minimum become 0.
    Values above maximum become 1.
    """
    if maximum <= minimum:
        raise ValueError(
            "Normalization maximum must be greater than minimum."
        )

    normalized = (
        (value - minimum)
        / (maximum - minimum)
    )

    return clamp(normalized)


def normalize_deficit(
    value: float,
    target: float,
) -> float:
    """
    Convert a positive environmental resource
    into a deficit score.

    0% coverage -> 1.0 deficit
    target coverage -> 0.0 deficit
    """
    if target <= 0:
        raise ValueError(
            "Deficit target must be greater than zero."
        )

    normalized = 1.0 - (
        value / target
    )

    return clamp(normalized)


# ============================================================
# INDIVIDUAL FACTOR NORMALIZATION
# ============================================================

def normalize_temperature(
    temperature: float,
) -> float:
    """
    Normalize temperature into a 0-1 thermal-risk score.
    """
    return normalize_range(
        temperature,
        TEMPERATURE_MIN,
        TEMPERATURE_MAX,
    )


def normalize_tree_deficit(
    tree_percentage: float,
) -> float:
    """
    Convert satellite tree coverage into
    vegetation-deficit risk.
    """
    return normalize_deficit(
        tree_percentage,
        TREE_TARGET_PERCENT,
    )


def normalize_building_exposure(
    building_percentage: float,
) -> float:
    """
    Convert building coverage into
    built-surface exposure risk.
    """
    return normalize_range(
        building_percentage,
        0.0,
        BUILDING_MAX_PERCENT,
    )


def normalize_street_tree_deficit(
    street_tree_percentage: float,
) -> float:
    """
    Convert street-level tree coverage into
    vegetation/shade deficit.
    """
    return normalize_deficit(
        street_tree_percentage,
        STREET_TREE_TARGET_PERCENT,
    )


def normalize_sky_exposure(
    sky_percentage: float,
) -> float:
    """
    Convert visible sky percentage into
    street-level shade exposure.
    """
    return normalize_range(
        sky_percentage,
        SKY_MIN_PERCENT,
        SKY_MAX_PERCENT,
    )


# ============================================================
# PRIORITY CLASSIFICATION
# ============================================================

def classify_priority(
    score: float,
) -> str:
    """
    Convert the final 0-100 score into
    a human-readable priority category.
    """
    if score >= 75:
        return "Critical"

    if score >= 50:
        return "High"

    if score >= 25:
        return "Moderate"

    return "Low"


# ============================================================
# MAIN TILE SCORING FUNCTION
# ============================================================

def calculate_tile_score(
    *,
    temperature: float | None,
    satellite_tree_percentage: float | None,
    building_percentage: float | None,
    street_tree_percentage: float | None,
    sky_percentage: float | None,
) -> dict[str, Any]:
    """
    Calculate TreeROI's transparent 0-100
    intervention-priority score.

    Missing values are NOT replaced with fake values.

    Only available factors contribute to the score.
    Their original weights are renormalized so that
    the available factors still produce a 0-100 score.

    Example:

        Temperature = available (40)
        Tree deficit = unavailable (25)
        Built surface = available (20)
        Street shade = available (15)

    Available weight = 75.

    The available contributions are scaled back to
    a 100-point score.
    """

    normalized_factors: dict[str, float | None] = {
        "temperature": None,
        "tree_deficit": None,
        "built_surface": None,
        "street_tree_deficit": None,
        "sky_exposure": None,
        "street_shade": None,
    }

    weighted_contributions: dict[str, float] = {}

    available_weights: dict[str, float] = {}

    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    if temperature is not None:
        temperature_score = normalize_temperature(
            temperature
        )

        normalized_factors["temperature"] = (
            temperature_score
        )

        available_weights["temperature"] = (
            TEMPERATURE_WEIGHT
        )

    # --------------------------------------------------------
    # Satellite tree deficit
    # --------------------------------------------------------

    if satellite_tree_percentage is not None:
        tree_deficit_score = normalize_tree_deficit(
            satellite_tree_percentage
        )

        normalized_factors["tree_deficit"] = (
            tree_deficit_score
        )

        available_weights["tree_deficit"] = (
            TREE_DEFICIT_WEIGHT
        )

    # --------------------------------------------------------
    # Built surface
    # --------------------------------------------------------

    if building_percentage is not None:
        building_score = normalize_building_exposure(
            building_percentage
        )

        normalized_factors["built_surface"] = (
            building_score
        )

        available_weights["built_surface"] = (
            BUILT_SURFACE_WEIGHT
        )

    # --------------------------------------------------------
    # Street-level shade
    #
    # Street shade is composed of:
    #
    #   70% street-tree deficit
    #   30% sky exposure
    #
    # If only one is available, that available component
    # is used rather than inventing the missing value.
    # --------------------------------------------------------

    street_tree_score: float | None = None
    sky_score: float | None = None

    if street_tree_percentage is not None:
        street_tree_score = normalize_street_tree_deficit(
            street_tree_percentage
        )

        normalized_factors["street_tree_deficit"] = (
            street_tree_score
        )

    if sky_percentage is not None:
        sky_score = normalize_sky_exposure(
            sky_percentage
        )

        normalized_factors["sky_exposure"] = (
            sky_score
        )

    if (
        street_tree_score is not None
        and sky_score is not None
    ):
        street_shade_score = (
            0.70 * street_tree_score
            + 0.30 * sky_score
        )

    elif street_tree_score is not None:
        street_shade_score = street_tree_score

    elif sky_score is not None:
        street_shade_score = sky_score

    else:
        street_shade_score = None

    if street_shade_score is not None:
        normalized_factors["street_shade"] = (
            street_shade_score
        )

        available_weights["street_shade"] = (
            STREET_SHADE_WEIGHT
        )

    # --------------------------------------------------------
    # No usable scoring data
    # --------------------------------------------------------

    available_weight_total = sum(
        available_weights.values()
    )

    if available_weight_total <= 0:
        return {
            "score": None,
            "priority": "Unknown",
            "data_completeness": 0.0,
            "available_weight": 0.0,
            "missing_factors": [
                "temperature",
                "tree_deficit",
                "built_surface",
                "street_shade",
            ],
            "weights": {
                "temperature": TEMPERATURE_WEIGHT,
                "tree_deficit": TREE_DEFICIT_WEIGHT,
                "built_surface": BUILT_SURFACE_WEIGHT,
                "street_shade": STREET_SHADE_WEIGHT,
            },
            "normalized_factors": normalized_factors,
            "weighted_contributions": {},
        }

    # --------------------------------------------------------
    # Calculate original weighted contributions
    # --------------------------------------------------------

    if normalized_factors["temperature"] is not None:
        weighted_contributions["temperature"] = (
            normalized_factors["temperature"]
            * TEMPERATURE_WEIGHT
        )

    if normalized_factors["tree_deficit"] is not None:
        weighted_contributions["tree_deficit"] = (
            normalized_factors["tree_deficit"]
            * TREE_DEFICIT_WEIGHT
        )

    if normalized_factors["built_surface"] is not None:
        weighted_contributions["built_surface"] = (
            normalized_factors["built_surface"]
            * BUILT_SURFACE_WEIGHT
        )

    if normalized_factors["street_shade"] is not None:
        weighted_contributions["street_shade"] = (
            normalized_factors["street_shade"]
            * STREET_SHADE_WEIGHT
        )

    # --------------------------------------------------------
    # Renormalize available weights to 100
    # --------------------------------------------------------

    scaling_factor = (
        TOTAL_WEIGHT
        / available_weight_total
    )

    total_score = sum(
        weighted_contributions.values()
    ) * scaling_factor

    total_score = round(
        clamp(total_score, 0.0, 100.0),
        2,
    )

    # --------------------------------------------------------
    # Missing factors
    # --------------------------------------------------------

    expected_factors = {
        "temperature",
        "tree_deficit",
        "built_surface",
        "street_shade",
    }

    available_factors = set(
        available_weights.keys()
    )

    missing_factors = sorted(
        expected_factors - available_factors
    )

    # --------------------------------------------------------
    # Data completeness
    #
    # This refers to the four scoring categories,
    # not to the optional environmental endpoint.
    # --------------------------------------------------------

    data_completeness = round(
        (
            len(available_factors)
            / len(expected_factors)
        ) * 100,
        1,
    )

    # --------------------------------------------------------
    # Return transparent scoring breakdown
    # --------------------------------------------------------

    return {
        "score": total_score,
        "priority": classify_priority(total_score),

        "data_completeness": data_completeness,

        "available_weight": round(
            available_weight_total,
            2,
        ),

        "missing_factors": missing_factors,

        "weights": {
            "temperature": TEMPERATURE_WEIGHT,
            "tree_deficit": TREE_DEFICIT_WEIGHT,
            "built_surface": BUILT_SURFACE_WEIGHT,
            "street_shade": STREET_SHADE_WEIGHT,
        },

        "normalized_factors": {
            key: (
                round(value, 3)
                if value is not None
                else None
            )
            for key, value
            in normalized_factors.items()
        },

        "weighted_contributions": {
            key: round(
                value * scaling_factor,
                2,
            )
            for key, value
            in weighted_contributions.items()
        },
    }
