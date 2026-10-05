import datetime
from app.models.database import get_db_connection

class AlertService:
    def evaluate_and_generate_alerts(self, locations_telemetry):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Deactivate old active alerts
        cursor.execute("UPDATE alerts SET is_active = 0 WHERE is_active = 1")
        
        generated_alerts = []
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in locations_telemetry:
            loc_id = item["location_id"]
            loc_name = item["location_name"]
            v_count = item["vehicle_count"]
            speed = item["traffic_speed"]
            aqi = item["aqi"]
            rain = item["rainfall"]
            water = item["water_level"]
            traffic_pred = item["traffic_pred"]
            flood_pred = item["flood_pred"]

            # 1. Traffic Congestion Alerts
            if v_count > 130 or speed < 18 or traffic_pred in ["High", "Critical"]:
                severity = "Critical" if (v_count > 160 or speed < 12 or traffic_pred == "Critical") else "Warning"
                msg = f"High traffic congestion detected at {loc_name} ({v_count} veh/min, avg {speed} km/h)."
                
                cursor.execute(
                    """
                    INSERT INTO alerts (location_id, alert_type, severity, message, is_active, timestamp)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (loc_id, "Traffic Congestion", severity, msg, now_str)
                )
                generated_alerts.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "alert_type": "Traffic Congestion",
                    "severity": severity,
                    "message": msg,
                    "timestamp": now_str
                })

            # 2. Flood Risk Alerts
            if rain > 45 or water > 2.0 or flood_pred in ["High", "Critical"]:
                severity = "Critical" if (rain > 80 or water > 3.0 or flood_pred == "Critical") else "Warning"
                msg = f"Potential flooding warning near {loc_name} (Rainfall: {rain}mm, Water Level: {water}m)."
                
                cursor.execute(
                    """
                    INSERT INTO alerts (location_id, alert_type, severity, message, is_active, timestamp)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (loc_id, "Flood Warning", severity, msg, now_str)
                )
                generated_alerts.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "alert_type": "Flood Warning",
                    "severity": severity,
                    "message": msg,
                    "timestamp": now_str
                })

            # 3. Air Quality Alerts
            if aqi > 100:
                severity = "Critical" if aqi > 150 else "Warning"
                msg = f"Poor air quality detected at {loc_name} (AQI {aqi}). Sensitive groups take caution."
                
                cursor.execute(
                    """
                    INSERT INTO alerts (location_id, alert_type, severity, message, is_active, timestamp)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (loc_id, "Air Quality", severity, msg, now_str)
                )
                generated_alerts.append({
                    "location_id": loc_id,
                    "location_name": loc_name,
                    "alert_type": "Air Quality",
                    "severity": severity,
                    "message": msg,
                    "timestamp": now_str
                })

        conn.commit()
        conn.close()
        return generated_alerts

alert_service = AlertService()
