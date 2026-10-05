"""
Central Data Ingestion Pipeline Service
---------------------------------------
Orchestrates:
1. OpenWeather API (Weather, Temperature, Rainfall)
2. OpenAQ API (Pollutant telemetry & CPCB AQI)
3. TomTom API (Real-time speed, travel time, delay, congestion)
4. Hydrological Simulator (Controlled water-level responding to rainfall)
5. Data Normalization & Validation
6. SQLite Timestamped Observation Persistence
7. Random Forest ML Inferences (predict_proba distributions)
8. Multi-modal Risk Calculation & Threshold Alert Generation

Supports strict separation between LIVE MODE (real APIs) and DEMO MODE (controlled demonstration scenarios).
"""

import datetime
from typing import Dict, List, Any, Optional

from app.models.database import get_db_connection
from app.services.weather_service import weather_service
from app.services.air_quality_service import air_quality_service
from app.services.traffic_service import traffic_service
from app.services.water_level_service import water_level_service
from app.services.prediction_service import prediction_service
from app.services.risk_service import calculate_location_risk, calculate_city_overall_risk
from app.services.alert_service import alert_service

def _get_status_color(risk_label: str) -> str:
    if risk_label in ["Low"]:
        return "green"
    elif risk_label in ["Moderate"]:
        return "yellow"
    else:
        return "red"

class DataIngestionService:
    def __init__(self):
        self.app_mode: str = "LIVE"  # "LIVE" or "DEMO"
        self.demo_scenario: str = "normal"  # "normal", "rush_hour", "heavy_rain"
        self._last_ingest_time: Optional[str] = None

    def set_mode(self, mode: str, scenario: Optional[str] = None) -> Dict[str, Any]:
        """Switches between LIVE MODE and DEMO MODE."""
        if mode.upper() in ["LIVE", "DEMO"]:
            self.app_mode = mode.upper()
        if scenario in ["normal", "rush_hour", "heavy_rain"]:
            self.demo_scenario = scenario
            
        # Ingest state under new mode
        self.ingest_data(force_refresh=(self.app_mode == "LIVE"))
        return {
            "mode": self.app_mode,
            "demo_scenario": self.demo_scenario,
            "is_live": self.app_mode == "LIVE"
        }

    def ingest_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Executes complete ingestion pipeline and stores timestamped observations.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM locations")
        locations = cursor.fetchall()
        now_dt = datetime.datetime.now()
        timestamp_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        hour = now_dt.hour
        day_of_week = now_dt.weekday()

        telemetry_records = []

        if self.app_mode == "LIVE":
            # 1. Fetch real OpenWeather
            weather = weather_service.fetch_weather(force_refresh=force_refresh)
            # Store in weather_data
            cursor.execute("""
                INSERT INTO weather_data (source, city, temperature, feels_like, humidity, pressure, rainfall, weather_condition, weather_details, wind_speed, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                weather.get("source", "openweather"),
                weather.get("city", "Coimbatore"),
                weather.get("temperature", 28.0),
                weather.get("feels_like", 28.0),
                weather.get("humidity", 60.0),
                weather.get("pressure", 1012),
                weather.get("rainfall", 0.0),
                weather.get("weather_condition", "Clear"),
                weather.get("weather_details", ""),
                weather.get("wind_speed", 0.0),
                weather.get("status", "connected"),
                timestamp_str
            ))

            # 2. Fetch real OpenAQ
            air = air_quality_service.fetch_air_quality(force_refresh=force_refresh)
            cursor.execute("""
                INSERT INTO air_quality_data (source, station_id, location_name, pm25, pm10, no2, o3, co, so2, aqi, aqi_category, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                air.get("source", "openaq"),
                air.get("station_id", 8914),
                air.get("location", "Coimbatore Station"),
                air.get("pm25"),
                air.get("pm10"),
                air.get("no2"),
                air.get("o3"),
                air.get("co"),
                air.get("so2"),
                air.get("aqi", 60),
                air.get("aqi_category", "Moderate"),
                air.get("status", "connected"),
                timestamp_str
            ))

            # 3. For each location, fetch real TomTom traffic and hydrological water level
            for loc in locations:
                loc_id = loc["id"]
                lat = float(loc["lat"])
                lng = float(loc["lng"])

                traffic = traffic_service.fetch_traffic_for_point(loc_id, lat, lng, force_refresh=force_refresh)
                
                # Store in traffic_data
                cursor.execute("""
                    INSERT INTO traffic_data (location_id, source, current_speed, free_flow_speed, delay_seconds, congestion_percentage, traffic_condition, road_closure, tomtom_confidence, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    loc_id,
                    traffic.get("source", "tomtom"),
                    traffic.get("current_speed", 30.0),
                    traffic.get("free_flow_speed", 45.0),
                    traffic.get("delay_seconds", 0),
                    traffic.get("congestion_percentage", 20.0),
                    traffic.get("traffic_condition", "Moderate"),
                    1 if traffic.get("road_closure") else 0,
                    traffic.get("tomtom_confidence", 0.9),
                    traffic.get("status", "connected"),
                    timestamp_str
                ))

                # Water level from physical basin simulator responding to rainfall
                water_res = water_level_service.get_water_level(loc_id, current_rainfall=weather.get("rainfall", 0.0))
                water_val = water_res["water_level"]

                # 4. ML Predictions
                t_pred, t_prob, t_dist = prediction_service.predict_traffic(
                    current_speed=traffic.get("current_speed", 30.0),
                    free_flow_speed=traffic.get("free_flow_speed", 45.0),
                    congestion_percentage=traffic.get("congestion_percentage", 20.0),
                    temperature=weather.get("temperature", 28.0),
                    rainfall=weather.get("rainfall", 0.0),
                    humidity=weather.get("humidity", 60.0),
                    aqi=air.get("aqi", 60),
                    hour=hour,
                    day_of_week=day_of_week
                )

                f_pred, f_prob, f_dist = prediction_service.predict_flood(
                    rainfall=weather.get("rainfall", 0.0),
                    water_level=water_val,
                    temperature=weather.get("temperature", 28.0),
                    humidity=weather.get("humidity", 60.0)
                )

                # 5. Composite Risk Calculation
                risk_score, risk_label = calculate_location_risk(
                    traffic_pred=t_pred,
                    flood_pred=f_pred,
                    aqi=air.get("aqi", 60),
                    water_level=water_val,
                    rainfall=weather.get("rainfall", 0.0),
                    congestion_percentage=traffic.get("congestion_percentage", 20.0)
                )

                # 6. Save in sensor_data unified snapshot
                cursor.execute("""
                    INSERT INTO sensor_data (
                        location_id, vehicle_count, traffic_speed, current_speed, free_flow_speed,
                        congestion_percentage, traffic_level, traffic_source, aqi, aqi_category,
                        aqi_source, temperature, humidity, rainfall, weather_condition, weather_source,
                        water_level, water_level_source, is_demo, demo_scenario, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?)
                """, (
                    loc_id,
                    0, # Real API mode does not fake vehicle counts
                    traffic.get("current_speed", 30.0),
                    traffic.get("current_speed", 30.0),
                    traffic.get("free_flow_speed", 45.0),
                    traffic.get("congestion_percentage", 20.0),
                    traffic.get("traffic_level", "Moderate"),
                    "tomtom",
                    air.get("aqi", 60),
                    air.get("aqi_category", "Moderate"),
                    "openaq",
                    weather.get("temperature", 28.0),
                    weather.get("humidity", 60.0),
                    weather.get("rainfall", 0.0),
                    weather.get("weather_condition", "Clear"),
                    "openweather",
                    water_val,
                    "simulation",
                    timestamp_str
                ))

                # Save predictions
                cursor.execute("""
                    INSERT INTO predictions (
                        location_id, traffic_pred, traffic_confidence, traffic_probability,
                        flood_pred, flood_confidence, flood_probability, horizon_min, is_demo, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 30, 0, ?)
                """, (
                    loc_id, t_pred, t_prob, t_prob, f_pred, f_prob, f_prob, timestamp_str
                ))

                telemetry_records.append({
                    "location_id": loc_id,
                    "location_name": loc["name"],
                    "lat": loc["lat"],
                    "lng": loc["lng"],
                    "zone_type": loc["zone_type"],
                    "type": dict(loc).get("type", "traffic"),
                    "description": loc["description"],
                    "current_speed": traffic["current_speed"],
                    "traffic_speed": traffic["current_speed"],
                    "free_flow_speed": traffic["free_flow_speed"],
                    "delay_seconds": traffic["delay_seconds"],
                    "congestion_percentage": traffic["congestion_percentage"],
                    "traffic_level": traffic["traffic_level"],
                    "traffic_source": "TomTom Traffic API",
                    "traffic_status": traffic["status"],
                    "aqi": air["aqi"],
                    "aqi_category": air["aqi_category"],
                    "aqi_source": "OpenAQ (Coimbatore Station)",
                    "pm25": air.get("pm25"),
                    "pm10": air.get("pm10"),
                    "no2": air.get("no2"),
                    "o3": air.get("o3"),
                    "co": air.get("co"),
                    "aqi_status": air["status"],
                    "temperature": weather["temperature"],
                    "feels_like": weather["feels_like"],
                    "humidity": weather["humidity"],
                    "rainfall": weather["rainfall"],
                    "weather_condition": weather["weather_condition"],
                    "weather_source": "OpenWeather (City-wide)",
                    "weather_status": weather["status"],
                    "water_level": water_val,
                    "water_level_source": "Hydrological Basin Simulation",
                    "traffic_pred": t_pred,
                    "traffic_probability": t_prob,
                    "traffic_confidence": t_prob,
                    "traffic_dist": t_dist,
                    "flood_pred": f_pred,
                    "flood_probability": f_prob,
                    "flood_confidence": f_prob,
                    "flood_dist": f_dist,
                    "horizon_min": 30,
                    "risk_score": risk_score,
                    "risk_label": risk_label,
                    "status_color": _get_status_color(risk_label),
                    "is_demo": False,
                    "timestamp": timestamp_str
                })

        else:
            # DEMO MODE: Controlled demonstration scenarios
            scenario = self.demo_scenario
            for loc in locations:
                loc_id = loc["id"]
                lat = float(loc["lat"])
                lng = float(loc["lng"])

                if scenario == "rush_hour":
                    # Severe rush hour congestion
                    free_flow_speed = 45.0
                    current_speed = round(11.0 + (5.0 if loc_id in ["airport-road"] else -2.0), 1)
                    current_speed = max(6.0, current_speed)
                    congestion_pct = round((free_flow_speed - current_speed) / free_flow_speed * 100.0, 1)
                    traffic_level = "Critical" if current_speed < 12.0 else "High"
                    delay_sec = 420
                    temp = 31.5
                    humidity = 58.0
                    rain = 0.0
                    weather_cond = "Clear"
                    aqi = 145 if loc_id == "industrial-area" else 115
                    aqi_cat = "Unhealthy for Sensitive Groups"
                    water_val = 0.85
                elif scenario == "heavy_rain":
                    # Severe rainfall and flood warning
                    free_flow_speed = 40.0
                    current_speed = 16.5
                    congestion_pct = 58.8
                    traffic_level = "High"
                    delay_sec = 310
                    temp = 23.0
                    humidity = 94.0
                    rain = 85.0 if loc_id == "river-zone" else 62.0
                    weather_cond = "Heavy Rain"
                    aqi = 35
                    aqi_cat = "Good"
                    water_res = water_level_service.get_water_level(loc_id, current_rainfall=rain, is_demo_scenario="heavy_rain")
                    water_val = water_res["water_level"]
                else:  # normal demo
                    free_flow_speed = 45.0
                    current_speed = 38.0
                    congestion_pct = 15.5
                    traffic_level = "Low"
                    delay_sec = 45
                    temp = 29.0
                    humidity = 62.0
                    rain = 0.0
                    weather_cond = "Clear"
                    aqi = 52
                    aqi_cat = "Moderate"
                    water_val = 0.75

                t_pred, t_prob, t_dist = prediction_service.predict_traffic(
                    current_speed=current_speed,
                    free_flow_speed=free_flow_speed,
                    congestion_percentage=congestion_pct,
                    temperature=temp,
                    rainfall=rain,
                    humidity=humidity,
                    aqi=aqi,
                    hour=hour,
                    day_of_week=day_of_week
                )

                f_pred, f_prob, f_dist = prediction_service.predict_flood(
                    rainfall=rain,
                    water_level=water_val,
                    temperature=temp,
                    humidity=humidity
                )

                risk_score, risk_label = calculate_location_risk(
                    traffic_pred=t_pred,
                    flood_pred=f_pred,
                    aqi=aqi,
                    water_level=water_val,
                    rainfall=rain,
                    congestion_percentage=congestion_pct
                )

                cursor.execute("""
                    INSERT INTO sensor_data (
                        location_id, vehicle_count, traffic_speed, current_speed, free_flow_speed,
                        congestion_percentage, traffic_level, traffic_source, aqi, aqi_category,
                        aqi_source, temperature, humidity, rainfall, weather_condition, weather_source,
                        water_level, water_level_source, is_demo, demo_scenario, timestamp
                    ) VALUES (?, 0, ?, ?, ?, ?, ?, 'demo_simulation', ?, ?, 'demo_simulation', ?, ?, ?, ?, 'demo_simulation', ?, 'demo_simulation', 1, ?, ?)
                """, (
                    loc_id, current_speed, current_speed, free_flow_speed, congestion_pct, traffic_level,
                    aqi, aqi_cat, temp, humidity, rain, weather_cond, water_val, scenario, timestamp_str
                ))

                telemetry_records.append({
                    "location_id": loc_id,
                    "location_name": loc["name"],
                    "lat": loc["lat"],
                    "lng": loc["lng"],
                    "zone_type": loc["zone_type"],
                    "type": dict(loc).get("type", "traffic"),
                    "description": loc["description"],
                    "current_speed": current_speed,
                    "traffic_speed": current_speed,
                    "free_flow_speed": free_flow_speed,
                    "delay_seconds": delay_sec,
                    "congestion_percentage": congestion_pct,
                    "traffic_level": traffic_level,
                    "traffic_source": "Demo Scenario Simulation",
                    "traffic_status": "demo",
                    "aqi": aqi,
                    "aqi_category": aqi_cat,
                    "aqi_source": "Demo Scenario Simulation",
                    "pm25": round(aqi * 0.6, 1),
                    "pm10": round(aqi * 0.8, 1),
                    "no2": None,
                    "o3": None,
                    "co": None,
                    "aqi_status": "demo",
                    "temperature": temp,
                    "feels_like": temp,
                    "humidity": humidity,
                    "rainfall": rain,
                    "weather_condition": weather_cond,
                    "weather_source": "Demo Scenario Simulation",
                    "weather_status": "demo",
                    "water_level": water_val,
                    "water_level_source": "Demo Scenario Simulation",
                    "traffic_pred": t_pred,
                    "traffic_probability": t_prob,
                    "traffic_confidence": t_prob,
                    "traffic_dist": t_dist,
                    "flood_pred": f_pred,
                    "flood_probability": f_prob,
                    "flood_confidence": f_prob,
                    "flood_dist": f_dist,
                    "horizon_min": 30,
                    "risk_score": risk_score,
                    "risk_label": risk_label,
                    "status_color": _get_status_color(risk_label),
                    "is_demo": True,
                    "demo_scenario": scenario,
                    "timestamp": timestamp_str
                })

        conn.commit()
        conn.close()

        self._last_ingest_time = timestamp_str
        return telemetry_records

    def get_current_telemetry(self) -> List[Dict[str, Any]]:
        """Returns the most recent normalized city telemetry."""
        # If no ingest has happened yet, run one
        if not self._last_ingest_time:
            return self.ingest_data()
        
        # Otherwise pull latest observations from SQLite
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM locations")
        locations = cursor.fetchall()
        
        results = []
        now_dt = datetime.datetime.now()
        hour = now_dt.hour
        day_of_week = now_dt.weekday()

        for loc in locations:
            loc_id = loc["id"]
            cursor.execute("""
                SELECT * FROM sensor_data 
                WHERE location_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (loc_id,))
            s = cursor.fetchone()

            if not s:
                conn.close()
                return self.ingest_data()

            s_dict = dict(s)
            
            # Predict
            t_pred, t_prob, t_dist = prediction_service.predict_traffic(
                current_speed=s_dict["current_speed"],
                free_flow_speed=s_dict["free_flow_speed"],
                congestion_percentage=s_dict["congestion_percentage"],
                temperature=s_dict["temperature"],
                rainfall=s_dict["rainfall"],
                humidity=s_dict["humidity"],
                aqi=s_dict["aqi"],
                hour=hour,
                day_of_week=day_of_week
            )

            f_pred, f_prob, f_dist = prediction_service.predict_flood(
                rainfall=s_dict["rainfall"],
                water_level=s_dict["water_level"],
                temperature=s_dict["temperature"],
                humidity=s_dict["humidity"]
            )

            risk_score, risk_label = calculate_location_risk(
                traffic_pred=t_pred,
                flood_pred=f_pred,
                aqi=s_dict["aqi"],
                water_level=s_dict["water_level"],
                rainfall=s_dict["rainfall"],
                congestion_percentage=s_dict["congestion_percentage"]
            )

            results.append({
                "location_id": loc_id,
                "location_name": loc["name"],
                "lat": loc["lat"],
                "lng": loc["lng"],
                "zone_type": loc["zone_type"],
                "type": dict(loc).get("type", "traffic"),
                "description": loc["description"],
                "current_speed": s_dict["current_speed"],
                "traffic_speed": s_dict["current_speed"],
                "free_flow_speed": s_dict["free_flow_speed"],
                "congestion_percentage": s_dict["congestion_percentage"],
                "traffic_level": s_dict["traffic_level"],
                "traffic_source": "TomTom Traffic API" if not s_dict.get("is_demo") else "Demo Scenario Simulation",
                "traffic_status": "connected" if not s_dict.get("is_demo") else "demo",
                "aqi": s_dict["aqi"],
                "aqi_category": s_dict["aqi_category"],
                "aqi_source": "OpenAQ (Coimbatore Station)" if not s_dict.get("is_demo") else "Demo Scenario Simulation",
                "temperature": s_dict["temperature"],
                "feels_like": s_dict["temperature"],
                "humidity": s_dict["humidity"],
                "rainfall": s_dict["rainfall"],
                "weather_condition": s_dict["weather_condition"],
                "weather_source": "OpenWeather (City-wide)" if not s_dict.get("is_demo") else "Demo Scenario Simulation",
                "water_level": s_dict["water_level"],
                "water_level_source": "Hydrological Basin Simulation" if not s_dict.get("is_demo") else "Demo Scenario Simulation",
                "traffic_pred": t_pred,
                "traffic_probability": t_prob,
                "traffic_confidence": t_prob,
                "traffic_dist": t_dist,
                "flood_pred": f_pred,
                "flood_probability": f_prob,
                "flood_confidence": f_prob,
                "flood_dist": f_dist,
                "horizon_min": 30,
                "risk_score": risk_score,
                "risk_label": risk_label,
                "status_color": _get_status_color(risk_label),
                "is_demo": bool(s_dict.get("is_demo")),
                "demo_scenario": s_dict.get("demo_scenario"),
                "timestamp": s_dict["timestamp"]
            })

        conn.close()
        return results

    def get_data_sources_status(self) -> List[Dict[str, Any]]:
        """Returns connectivity metadata for all external sources."""
        sources = [
            weather_service.get_source_status(),
            air_quality_service.get_source_status(),
            traffic_service.get_source_status(),
            {
                "name": "Water Level",
                "source": "simulation",
                "status": "simulated",
                "last_update": datetime.datetime.now().strftime("%I:%M:%S %p"),
                "update_interval": "Dynamic (Rainfall-driven)",
                "coverage": "8 Urban Catchment Zones",
                "note": "Water-level data is simulated because a reliable authorized real-time water-level source is not currently integrated."
            }
        ]
        return sources

data_ingestion_service = DataIngestionService()
