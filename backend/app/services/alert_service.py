import datetime
from typing import List, Dict, Any
from app.models.database import get_db_connection

class AlertService:
    def evaluate_and_generate_alerts(self, locations_telemetry: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates real-time multi-modal telemetry against operational thresholds.
        Persists active alerts in SQLite and returns active alerts list.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Reset previous active alerts
        cursor.execute("UPDATE alerts SET is_active = 0 WHERE is_active = 1")
        
        generated_alerts = []
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in locations_telemetry:
            loc_id = item["location_id"]
            loc_name = item.get("location_name", loc_id)
            speed = float(item.get("current_speed", item.get("traffic_speed", 30.0)))
            congestion_pct = float(item.get("congestion_percentage", 0.0))
            delay_sec = int(item.get("delay_seconds", 0))
            traffic_pred = item.get("traffic_pred", "Low")

            rain = float(item.get("rainfall", 0.0))
            water = float(item.get("water_level", 0.8))
            flood_pred = item.get("flood_pred", "Low")

            aqi = int(item.get("aqi", 50))
            aqi_cat = item.get("aqi_category", "Moderate")

            # 1. Traffic Congestion Alerts (From TomTom real speeds & congestion)
            if congestion_pct >= 40.0 or speed < 18.0 or traffic_pred in ["High", "Critical"]:
                severity = "Critical" if (congestion_pct >= 60.0 or speed < 12.0 or traffic_pred == "Critical") else "Warning"
                msg = f"High traffic congestion detected at {loc_name} (Speed: {speed} km/h, Delay: {delay_sec}s, Congestion: {congestion_pct}%)."
                source = "TomTom Traffic API"
                
                cursor.execute(
                    """
                    INSERT INTO alerts (location_id, alert_type, severity, message, source, is_active, timestamp)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    """,
                    (loc_id, "Traffic Congestion", severity, msg, source, now_str)
                )
                generated_alerts.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "alert_type": "Traffic Congestion",
                    "severity": severity,
                    "message": msg,
                    "source": source,
                    "timestamp": now_str
                })

            # 2. Flood Risk Alerts (From OpenWeather rain + water level)
            if rain >= 30.0 or water >= 1.8 or flood_pred in ["High", "Critical"]:
                severity = "Critical" if (rain >= 70.0 or water >= 2.8 or flood_pred == "Critical") else "Warning"
                msg = f"Potential flooding detected near {loc_name} (Rainfall: {rain} mm/h, Basin Level: {water}m)."
                source = "OpenWeather & Hydrology"
                
                cursor.execute(
                    """
                    INSERT INTO alerts (location_id, alert_type, severity, message, source, is_active, timestamp)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    """,
                    (loc_id, "Flood Warning", severity, msg, source, now_str)
                )
                generated_alerts.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "alert_type": "Flood Warning",
                    "severity": severity,
                    "message": msg,
                    "source": source,
                    "timestamp": now_str
                })

            # 3. Air Quality Alerts (From OpenAQ station observations)
            if aqi > 100 or aqi_cat in ["Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]:
                severity = "Critical" if aqi > 150 else "Warning"
                msg = f"Poor air quality detected at {loc_name} (AQI {aqi} - {aqi_cat}). Sensitive populations should take precautions."
                source = "OpenAQ Monitoring"
                
                cursor.execute(
                    """
                    INSERT INTO alerts (location_id, alert_type, severity, message, source, is_active, timestamp)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    """,
                    (loc_id, "Air Quality", severity, msg, source, now_str)
                )
                generated_alerts.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "alert_type": "Air Quality",
                    "severity": severity,
                    "message": msg,
                    "source": source,
                    "timestamp": now_str
                })

        conn.commit()
        conn.close()
        return generated_alerts

alert_service = AlertService()
