from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

from app.models.database import get_db_connection
from app.services.sensor_service import sensor_service
from app.services.prediction_service import prediction_service
from app.services.risk_service import calculate_location_risk, calculate_city_overall_risk
from app.services.alert_service import alert_service

router = APIRouter()

class SimulationRequest(BaseModel):
    scenario: Optional[str] = "normal"

class CustomPredictionRequest(BaseModel):
    vehicle_count: int
    traffic_speed: float
    aqi: int
    temperature: float
    rainfall: float
    water_level: float
    prev_rainfall: Optional[float] = 0.0

def _get_aqi_category(aqi: int) -> str:
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    else:
        return "Unhealthy"

def _get_status_color(risk_label: str) -> str:
    if risk_label in ["Low"]:
        return "green"
    elif risk_label in ["Moderate"]:
        return "yellow"
    else:
        return "red"

def _build_city_telemetry_state():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()

    if not locations:
        conn.close()
        return []

    telemetry = []

    for loc in locations:
        loc_id = loc["id"]
        cursor.execute(
            "SELECT * FROM sensor_data WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1",
            (loc_id,)
        )
        s = cursor.fetchone()

        if not s:
            # Trigger initial tick if database is empty
            sensor_service.generate_sensor_tick("normal")
            cursor.execute(
                "SELECT * FROM sensor_data WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1",
                (loc_id,)
            )
            s = cursor.fetchone()

        now = datetime.datetime.now()
        hour = now.hour
        day_of_week = now.weekday()

        # ML Predictions
        t_pred, t_conf = prediction_service.predict_traffic(
            vehicle_count=s["vehicle_count"],
            traffic_speed=s["traffic_speed"],
            hour=hour,
            day_of_week=day_of_week,
            aqi=s["aqi"],
            temperature=s["temperature"],
            rainfall=s["rainfall"]
        )

        f_pred, f_conf = prediction_service.predict_flood(
            rainfall=s["rainfall"],
            water_level=s["water_level"],
            temperature=s["temperature"],
            prev_rainfall=0.0
        )

        risk_score, risk_label = calculate_location_risk(
            traffic_pred=t_pred,
            flood_pred=f_pred,
            aqi=s["aqi"],
            water_level=s["water_level"],
            rainfall=s["rainfall"]
        )

        telemetry.append({
            "location_id": loc_id,
            "location_name": loc["name"],
            "lat": loc["lat"],
            "lng": loc["lng"],
            "zone_type": loc["zone_type"],
            "description": loc["description"],
            "vehicle_count": s["vehicle_count"],
            "traffic_speed": s["traffic_speed"],
            "traffic_level": s["traffic_level"],
            "aqi": s["aqi"],
            "aqi_category": _get_aqi_category(s["aqi"]),
            "temperature": s["temperature"],
            "rainfall": s["rainfall"],
            "water_level": s["water_level"],
            "traffic_pred": t_pred,
            "traffic_confidence": t_conf,
            "flood_pred": f_pred,
            "flood_confidence": f_conf,
            "horizon_min": 30,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "status_color": _get_status_color(risk_label),
            "timestamp": s["timestamp"]
        })

    conn.close()
    return telemetry

@router.get("/city/status")
def get_city_status():
    telemetry = _build_city_telemetry_state()
    
    # Evaluate alerts
    active_alerts = alert_service.evaluate_and_generate_alerts(telemetry)
    
    avg_traffic = int(sum(t["vehicle_count"] for t in telemetry) / max(1, len(telemetry)))
    avg_aqi = int(sum(t["aqi"] for t in telemetry) / max(1, len(telemetry)))
    
    # Overall city traffic status
    traffic_preds = [t["traffic_pred"] for t in telemetry]
    if "Critical" in traffic_preds:
        overall_traffic = "Critical"
    elif traffic_preds.count("High") >= 2:
        overall_traffic = "High"
    elif "High" in traffic_preds or traffic_preds.count("Moderate") >= 3:
        overall_traffic = "Moderate"
    else:
        overall_traffic = "Low"

    # Overall flood risk
    flood_preds = [t["flood_pred"] for t in telemetry]
    if "Critical" in flood_preds:
        overall_flood = "Critical"
    elif flood_preds.count("High") >= 2:
        overall_flood = "High"
    elif "High" in flood_preds or flood_preds.count("Moderate") >= 3:
        overall_flood = "Moderate"
    else:
        overall_flood = "Low"

    overall_risk_score, overall_risk_label = calculate_city_overall_risk(telemetry)

    return {
        "system_status": "Online",
        "last_updated": datetime.datetime.now().strftime("%I:%M:%S %p"),
        "current_scenario": sensor_service.current_scenario,
        "traffic_status": overall_traffic,
        "avg_traffic": f"{avg_traffic} vehicles/min",
        "avg_traffic_val": avg_traffic,
        "aqi_display": f"AQI {avg_aqi}",
        "aqi_val": avg_aqi,
        "aqi_category": _get_aqi_category(avg_aqi),
        "flood_risk": overall_flood,
        "active_alerts_count": len(active_alerts),
        "overall_risk_score": overall_risk_score,
        "overall_risk_label": overall_risk_label,
        "overall_status_color": _get_status_color(overall_risk_label)
    }

@router.get("/locations")
def get_locations():
    return _build_city_telemetry_state()

@router.get("/location/{location_id}")
def get_location_detail(location_id: str):
    telemetry = _build_city_telemetry_state()
    for item in telemetry:
        if item["location_id"] == location_id:
            return item
    raise HTTPException(status_code=404, detail="Location not found")

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
    telemetry = _build_city_telemetry_state()
    preds = []
    for item in telemetry:
        preds.append({
            "location_id": item["location_id"],
            "location_name": item["location_name"],
            "current_traffic": item["traffic_level"],
            "predicted_traffic": item["traffic_pred"],
            "traffic_confidence": item["traffic_confidence"],
            "current_flood_risk": item["flood_pred"],
            "predicted_flood_risk": item["flood_pred"],
            "flood_confidence": item["flood_confidence"],
            "prediction_horizon": "30 minutes"
        })
    return preds

@router.get("/alerts")
def get_alerts():
    telemetry = _build_city_telemetry_state()
    return alert_service.evaluate_and_generate_alerts(telemetry)

@router.get("/analytics")
def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query last 20 timestamps aggregated across city
    cursor.execute("""
        SELECT 
            strftime('%H:%M:%S', timestamp) as time_label,
            ROUND(AVG(vehicle_count)) as avg_vehicles,
            ROUND(AVG(aqi)) as avg_aqi,
            ROUND(AVG(rainfall)) as avg_rainfall
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
        v = r_dict["avg_vehicles"]
        a = r_dict["avg_aqi"]
        risk_est = min(100, max(10, int((v * 0.4) + (a * 0.4))))
        r_dict["risk_score"] = risk_est
        result.append(r_dict)

    return result

@router.post("/simulate")
def trigger_simulation(req: Optional[SimulationRequest] = None):
    scenario = req.scenario if req else "normal"
    sensor_service.set_scenario(scenario)
    new_readings = sensor_service.generate_sensor_tick(scenario)
    
    telemetry = _build_city_telemetry_state()
    alerts = alert_service.evaluate_and_generate_alerts(telemetry)
    
    return {
        "status": "success",
        "scenario": scenario,
        "generated_readings_count": len(new_readings),
        "alerts_count": len(alerts),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@router.post("/predict")
def custom_predict(req: CustomPredictionRequest):
    now = datetime.datetime.now()
    t_pred, t_conf = prediction_service.predict_traffic(
        vehicle_count=req.vehicle_count,
        traffic_speed=req.traffic_speed,
        hour=now.hour,
        day_of_week=now.weekday(),
        aqi=req.aqi,
        temperature=req.temperature,
        rainfall=req.rainfall
    )

    f_pred, f_conf = prediction_service.predict_flood(
        rainfall=req.rainfall,
        water_level=req.water_level,
        temperature=req.temperature,
        prev_rainfall=req.prev_rainfall
    )

    risk_score, risk_label = calculate_location_risk(t_pred, f_pred, req.aqi, req.water_level, req.rainfall)

    return {
        "predicted_traffic_level": t_pred,
        "traffic_confidence": t_conf,
        "predicted_flood_risk": f_pred,
        "flood_confidence": f_conf,
        "composite_risk_score": risk_score,
        "composite_risk_label": risk_label
    }
