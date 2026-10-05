"""
Dynamic Risk Engine
-------------------
Calculates composite risk scores (0 - 100) based on real multi-modal telemetry:
- Traffic Risk (40%)
- Flood Risk (40%)
- Air Quality Risk (20%)
Configurable thresholds categorize risk into Low, Moderate, High, Critical.
"""

from typing import Tuple, List, Dict, Any

LEVEL_WEIGHTS = {
    "Low": 15,
    "Normal": 15,
    "Moderate": 40,
    "High": 70,
    "Critical": 95
}

# Configurable weights
TRAFFIC_WEIGHT = 0.40
FLOOD_WEIGHT = 0.40
AQI_WEIGHT = 0.20

# Configurable thresholds
THRESHOLDS = {
    "low_max": 25,
    "moderate_max": 50,
    "high_max": 75
}

def calculate_location_risk(
    traffic_pred: str,
    flood_pred: str,
    aqi: int,
    water_level: float,
    rainfall: float,
    congestion_percentage: float = 0.0
) -> Tuple[int, str]:
    """
    Computes weighted risk score and categorical label for an urban zone.
    """
    t_score = LEVEL_WEIGHTS.get(traffic_pred, 25)
    # Factor in raw congestion percentage if severe
    if congestion_percentage >= 60.0:
        t_score = max(t_score, 85)

    f_score = LEVEL_WEIGHTS.get(flood_pred, 20)
    # Factor in water level surge
    if water_level >= 2.5 or rainfall >= 50.0:
        f_score = max(f_score, 85)

    # AQI score mapping (0 - 100)
    if aqi <= 50:
        aqi_score = 10
    elif aqi <= 100:
        aqi_score = 35
    elif aqi <= 150:
        aqi_score = 65
    elif aqi <= 250:
        aqi_score = 85
    else:
        aqi_score = 100

    composite = (t_score * TRAFFIC_WEIGHT) + (f_score * FLOOD_WEIGHT) + (aqi_score * AQI_WEIGHT)
    composite_score = min(100, max(0, int(round(composite))))

    if composite_score <= THRESHOLDS["low_max"]:
        risk_label = "Low"
    elif composite_score <= THRESHOLDS["moderate_max"]:
        risk_label = "Moderate"
    elif composite_score <= THRESHOLDS["high_max"]:
        risk_label = "High"
    else:
        risk_label = "Critical"

    return composite_score, risk_label

def calculate_city_overall_risk(location_metrics: List[Dict[str, Any]]) -> Tuple[int, str]:
    """
    Calculates city-wide aggregate risk across all monitored zones.
    """
    if not location_metrics:
        return 20, "Low"

    scores = [m.get("risk_score", 20) for m in location_metrics]
    overall_score = round(sum(scores) / len(scores))

    if overall_score <= THRESHOLDS["low_max"]:
        status = "Low"
    elif overall_score <= THRESHOLDS["moderate_max"]:
        status = "Moderate"
    elif overall_score <= THRESHOLDS["high_max"]:
        status = "High"
    else:
        status = "Critical"

    return overall_score, status
