from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

from app.models.database import get_db_connection
from app.services.weather_service import weather_service
from app.services.air_quality_service import air_quality_service
from app.services.traffic_service import traffic_service
from app.services.water_level_service import water_level_service
from app.services.prediction_service import prediction_service
from app.services.risk_service import calculate_location_risk, calculate_city_overall_risk
from app.services.alert_service import alert_service
from app.services.data_ingestion_service import data_ingestion_service, _get_status_color

router = APIRouter()

class SimulationRequest(BaseModel):
    mode: Optional[str] = "DEMO"          # "LIVE" or "DEMO"
    scenario: Optional[str] = "normal"    # "normal", "rush_hour", "heavy_rain"

class CustomPredictionRequest(BaseModel):
    current_speed: float = 30.0
    free_flow_speed: float = 45.0
    congestion_percentage: Optional[float] = None
    aqi: int = 60
    temperature: float = 28.0
    rainfall: float = 0.0
    humidity: Optional[float] = 60.0
    water_level: float = 0.8
    prev_rainfall: Optional[float] = 0.0

@router.get("/city/status")
def get_city_status():
    telemetry = data_ingestion_service.get_current_telemetry()
    active_alerts = alert_service.evaluate_and_generate_alerts(telemetry)

    # City-wide averages
    avg_speed = round(sum(t.get("current_speed", 30.0) for t in telemetry) / max(1, len(telemetry)), 1)
    avg_congestion = round(sum(t.get("congestion_percentage", 0.0) for t in telemetry) / max(1, len(telemetry)), 1)
    avg_aqi = int(round(sum(t.get("aqi", 50) for t in telemetry) / max(1, len(telemetry))))
    avg_rainfall = round(sum(t.get("rainfall", 0.0) for t in telemetry) / max(1, len(telemetry)), 2)
    avg_temp = round(sum(t.get("temperature", 28.0) for t in telemetry) / max(1, len(telemetry)), 1)

    # Overall traffic status
    traffic_preds = [t.get("traffic_pred", "Low") for t in telemetry]
    if "Critical" in traffic_preds or avg_congestion >= 60.0:
        overall_traffic = "Critical"
    elif traffic_preds.count("High") >= 2 or avg_congestion >= 40.0:
        overall_traffic = "High"
    elif "High" in traffic_preds or traffic_preds.count("Moderate") >= 3 or avg_congestion >= 20.0:
        overall_traffic = "Moderate"
    else:
        overall_traffic = "Normal"

    # Overall flood risk
    flood_preds = [t.get("flood_pred", "Low") for t in telemetry]
    if "Critical" in flood_preds or avg_rainfall >= 70.0:
        overall_flood = "Critical"
    elif flood_preds.count("High") >= 2 or avg_rainfall >= 35.0:
        overall_flood = "High"
    elif "High" in flood_preds or flood_preds.count("Moderate") >= 3 or avg_rainfall >= 10.0:
        overall_flood = "Moderate"
    else:
        overall_flood = "Low"

    overall_risk_score, overall_risk_label = calculate_city_overall_risk(telemetry)

    # Get sample AQI category
    sample_aqi_cat = telemetry[0].get("aqi_category", "Moderate") if telemetry else "Moderate"
    sample_weather_cond = telemetry[0].get("weather_condition", "Clear") if telemetry else "Clear"

    return {
        "system_status": "Online",
        "mode": data_ingestion_service.app_mode,
        "is_live": data_ingestion_service.app_mode == "LIVE",
        "demo_scenario": data_ingestion_service.demo_scenario if data_ingestion_service.app_mode == "DEMO" else None,
        "city_name": "Coimbatore",
        "last_updated": datetime.datetime.now().strftime("%I:%M:%S %p"),
        
        # Real Traffic Metrics
        "traffic_status": overall_traffic,
        "avg_speed_display": f"{avg_speed} km/h",
        "avg_speed_val": avg_speed,
        "avg_congestion_display": f"{avg_congestion}%",
        "avg_congestion_val": avg_congestion,
        
        # Real Air Quality
        "aqi_display": f"AQI {avg_aqi}",
        "aqi_val": avg_aqi,
        "aqi_category": sample_aqi_cat,
        
        # Real Weather & Rainfall
        "rainfall_display": f"{avg_rainfall} mm/h",
        "rainfall_val": avg_rainfall,
        "temperature_display": f"{avg_temp} °C",
        "temperature_val": avg_temp,
        "weather_condition": sample_weather_cond,
        
        # Flood & Risk
        "flood_risk": overall_flood,
        "active_alerts_count": len(active_alerts),
        "overall_risk_score": overall_risk_score,
        "overall_risk_label": overall_risk_label,
        "overall_status_color": _get_status_color(overall_risk_label),
        
        # Sources
        "data_sources": data_ingestion_service.get_data_sources_status()
    }

@router.get("/locations")
def get_locations():
    return data_ingestion_service.get_current_telemetry()

@router.get("/location/{location_id}")
def get_location_detail(location_id: str):
    telemetry = data_ingestion_service.get_current_telemetry()
    for item in telemetry:
        if item["location_id"] == location_id:
            return item
    raise HTTPException(status_code=404, detail="Location not found")

@router.get("/weather")
def get_weather():
    return weather_service.fetch_weather()

@router.get("/air-quality")
def get_air_quality():
    return air_quality_service.fetch_air_quality()

@router.get("/traffic")
def get_traffic():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, l.name as location_name 
        FROM traffic_data t 
        JOIN locations l ON t.location_id = l.id 
        ORDER BY t.timestamp DESC 
        LIMIT 8
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/sensors")
def get_sensor_snapshot():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, l.name as location_name 
        FROM sensor_data s 
        JOIN locations l ON s.location_id = l.id 
        ORDER BY s.timestamp DESC 
        LIMIT 8
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/predictions")
def get_predictions():
    telemetry = data_ingestion_service.get_current_telemetry()
    preds = []
    for item in telemetry:
        preds.append({
            "location_id": item["location_id"],
            "location_name": item["location_name"],
            "current_traffic": item["traffic_level"],
            "predicted_traffic": item["traffic_pred"],
            "traffic_confidence": item.get("traffic_probability", 85.0),
            "traffic_probability": item.get("traffic_probability", 85.0),
            "traffic_dist": item.get("traffic_dist", {}),
            "current_flood_risk": item["flood_pred"],
            "predicted_flood_risk": item["flood_pred"],
            "flood_confidence": item.get("flood_probability", 85.0),
            "flood_probability": item.get("flood_probability", 85.0),
            "flood_dist": item.get("flood_dist", {}),
            "prediction_horizon": "30 minutes",
            "is_demo": item.get("is_demo", False)
        })
    return preds

@router.get("/alerts")
def get_alerts():
    telemetry = data_ingestion_service.get_current_telemetry()
    return alert_service.evaluate_and_generate_alerts(telemetry)

@router.get("/analytics")
def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query last 20 timestamps aggregated across city
    cursor.execute("""
        SELECT 
            strftime('%H:%M:%S', timestamp) as time_label,
            ROUND(AVG(current_speed), 1) as avg_speed,
            ROUND(AVG(congestion_percentage), 1) as avg_congestion,
            ROUND(AVG(aqi)) as avg_aqi,
            ROUND(AVG(rainfall), 2) as avg_rainfall
        FROM sensor_data
        GROUP BY timestamp
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in reversed(rows):
        r_dict = dict(r)
        # Derive risk score estimate for chart
        c = r_dict["avg_congestion"] or 0
        a = r_dict["avg_aqi"] or 50
        r_rain = r_dict["avg_rainfall"] or 0
        risk_est = min(100, max(10, int((c * 0.45) + (a * 0.35) + (r_rain * 0.4))))
        r_dict["risk_score"] = risk_est
        result.append(r_dict)

    return result

@router.get("/data-sources/status")
def get_data_sources():
    return data_ingestion_service.get_data_sources_status()

@router.post("/simulate")
def trigger_simulation(req: Optional[SimulationRequest] = None):
    """
    Toggles between LIVE MODE and DEMO MODE.
    If req.mode == 'LIVE', initiates live API data ingestion.
    If req.mode == 'DEMO', executes controlled demonstration scenario (normal, rush_hour, heavy_rain).
    """
    mode = req.mode if req and req.mode else "DEMO"
    scenario = req.scenario if req and req.scenario else "normal"
    
    state = data_ingestion_service.set_mode(mode=mode, scenario=scenario)
    telemetry = data_ingestion_service.get_current_telemetry()
    alerts = alert_service.evaluate_and_generate_alerts(telemetry)

    return {
        "status": "success",
        "mode": state["mode"],
        "is_live": state["is_live"],
        "scenario": state["demo_scenario"],
        "locations_count": len(telemetry),
        "alerts_count": len(alerts),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@router.post("/predict")
def custom_predict(req: CustomPredictionRequest):
    now = datetime.datetime.now()
    congestion = req.congestion_percentage
    if congestion is None:
        congestion = max(0.0, (req.free_flow_speed - req.current_speed) / req.free_flow_speed * 100.0)

    t_pred, t_prob, t_dist = prediction_service.predict_traffic(
        current_speed=req.current_speed,
        free_flow_speed=req.free_flow_speed,
        congestion_percentage=congestion,
        temperature=req.temperature,
        rainfall=req.rainfall,
        humidity=req.humidity or 60.0,
        aqi=req.aqi,
        hour=now.hour,
        day_of_week=now.weekday()
    )

    f_pred, f_prob, f_dist = prediction_service.predict_flood(
        rainfall=req.rainfall,
        water_level=req.water_level,
        temperature=req.temperature,
        humidity=req.humidity or 60.0,
        prev_rainfall=req.prev_rainfall or 0.0
    )

    risk_score, risk_label = calculate_location_risk(
        traffic_pred=t_pred,
        flood_pred=f_pred,
        aqi=req.aqi,
        water_level=req.water_level,
        rainfall=req.rainfall,
        congestion_percentage=congestion
    )

    return {
        "predicted_traffic_level": t_pred,
        "traffic_probability": t_prob,
        "traffic_dist": t_dist,
        "predicted_flood_risk": f_pred,
        "flood_probability": f_prob,
        "flood_dist": f_dist,
        "composite_risk_score": risk_score,
        "composite_risk_label": risk_label
    }
