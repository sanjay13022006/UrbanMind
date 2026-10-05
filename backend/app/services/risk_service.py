def calculate_location_risk(traffic_pred, flood_pred, aqi, water_level, rainfall):
    # Severity numeric weights
    level_weights = {
        "Low": 15,
        "Moderate": 40,
        "High": 70,
        "Critical": 95
    }

    t_score = level_weights.get(traffic_pred, 20)
    f_score = level_weights.get(flood_pred, 20)
    
    # AQI score calculation (0 - 100 component)
    if aqi <= 50:
        aqi_score = 10
    elif aqi <= 100:
        aqi_score = 35
    elif aqi <= 150:
        aqi_score = 65
    else:
        aqi_score = 95

    # Weighted risk combination
    composite = (t_score * 0.40) + (f_score * 0.40) + (aqi_score * 0.20)
    composite_score = min(100, max(0, round(composite)))

    if composite_score <= 25:
        risk_label = "Low"
    elif composite_score <= 50:
        risk_label = "Moderate"
    elif composite_score <= 75:
        risk_label = "High"
    else:
        risk_label = "Critical"

    return composite_score, risk_label

def calculate_city_overall_risk(location_metrics):
    if not location_metrics:
        return 20, "Low"

    scores = [m.get("risk_score", 20) for m in location_metrics]
    overall_score = round(sum(scores) / len(scores))

    if overall_score <= 25:
        status = "Low"
    elif overall_score <= 50:
        status = "Moderate"
    elif overall_score <= 75:
        status = "High"
    else:
        status = "Critical"

    return overall_score, status
