"""
Automated Test Suite for UrbanTwin AI Data Pipeline
----------------------------------------------------
Tests:
1. OpenWeather API service & normalization
2. OpenAQ v3 API service & CPCB AQI calculation
3. TomTom Traffic API service & congestion calculation
4. Water Level Hydrological Simulation
5. API Failure & Stale Data Preservation Handling
6. Random Forest ML Inferences & Probability Distributions
7. Dynamic Risk Engine
8. Threshold Alert Engine
9. Central Data Ingestion Service
10. FastAPI REST Endpoints via TestClient
"""

import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.models.database import init_db, get_db_connection
from app.services.weather_service import weather_service
from app.services.air_quality_service import air_quality_service
from app.services.traffic_service import traffic_service
from app.services.water_level_service import water_level_service
from app.services.prediction_service import prediction_service
from app.services.risk_service import calculate_location_risk, calculate_city_overall_risk
from app.services.alert_service import alert_service
from app.services.data_ingestion_service import data_ingestion_service

class TestUrbanTwinPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- Initializing Test Environment & Database ---")
        init_db()

    def test_01_openweather_service(self):
        print("\n[Test 1] Testing OpenWeather Service...")
        data = weather_service.fetch_weather()
        self.assertIn("source", data)
        self.assertEqual(data["source"], "openweather")
        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("rainfall", data)
        self.assertIsInstance(data["temperature"], (int, float))
        self.assertIsInstance(data["rainfall"], (int, float))
        self.assertGreaterEqual(data["rainfall"], 0.0)
        print(f"  -> OpenWeather OK: {data['temperature']}°C, Rain: {data['rainfall']}mm, Status: {data['status']}")

    def test_02_openaq_service(self):
        print("\n[Test 2] Testing OpenAQ Service...")
        data = air_quality_service.fetch_air_quality()
        self.assertIn("source", data)
        self.assertEqual(data["source"], "openaq")
        self.assertIn("aqi", data)
        self.assertIn("aqi_category", data)
        self.assertGreater(data["aqi"], 0)
        self.assertIsNotNone(data["pm25"])
        print(f"  -> OpenAQ OK: PM2.5={data['pm25']}, AQI={data['aqi']} ({data['aqi_category']})")

    def test_03_tomtom_service(self):
        print("\n[Test 3] Testing TomTom Traffic Service...")
        data = traffic_service.fetch_traffic_for_point("central-junction", 11.0183, 76.9644)
        self.assertIn("source", data)
        self.assertEqual(data["source"], "tomtom")
        self.assertIn("current_speed", data)
        self.assertIn("free_flow_speed", data)
        self.assertIn("congestion_percentage", data)
        self.assertGreater(data["free_flow_speed"], 0)
        self.assertGreaterEqual(data["congestion_percentage"], 0.0)
        print(f"  -> TomTom OK: Speed={data['current_speed']} km/h, Congestion={data['congestion_percentage']}%, Condition={data['traffic_condition']}")

    def test_04_water_level_service(self):
        print("\n[Test 4] Testing Water Level Hydrological Service...")
        res_normal = water_level_service.get_water_level("river-zone", current_rainfall=0.0)
        self.assertEqual(res_normal["source"], "simulation")
        self.assertTrue(res_normal["is_simulated"])
        self.assertGreater(res_normal["water_level"], 0.0)
        
        # Test rainfall response: high rainfall should increase water level
        res_rain = water_level_service.get_water_level("river-zone", current_rainfall=80.0)
        self.assertGreater(res_rain["water_level"], res_normal["water_level"])
        print(f"  -> Water Level OK: Normal={res_normal['water_level']}m -> Rain Response={res_rain['water_level']}m (Simulated)")

    def test_05_api_failure_handling(self):
        print("\n[Test 5] Testing Failure Handling without Fake Replacement Data...")
        orig_cached = weather_service._cached_data
        orig_fetch_time = weather_service._last_fetch_time
        old_key = weather_service.api_key

        # Set valid cached observation
        weather_service._cached_data = {
            "source": "openweather",
            "status": "connected",
            "temperature": 29.5,
            "rainfall": 0.0,
            "humidity": 55.0,
            "weather_condition": "Clouds",
            "timestamp": "2026-10-05 10:00:00"
        }
        weather_service._last_fetch_time = 0

        # Simulate API failure / key missing
        weather_service.api_key = ""
        stale_result = weather_service.fetch_weather(force_refresh=True)
        self.assertEqual(stale_result["status"], "stale")
        self.assertIn("warning", stale_result)
        self.assertEqual(stale_result["temperature"], 29.5)

        # Restore original state
        weather_service.api_key = old_key
        weather_service._cached_data = orig_cached
        weather_service._last_fetch_time = orig_fetch_time
        print("  -> Failure Handling OK: Stale cache preserved with explicit warning flag.")

    def test_06_ml_predictions(self):
        print("\n[Test 6] Testing Random Forest ML Inferences & Probabilities...")
        t_pred, t_prob, t_dist = prediction_service.predict_traffic(
            current_speed=18.0,
            free_flow_speed=40.0,
            congestion_percentage=55.0,
            temperature=30.0,
            rainfall=2.0,
            humidity=60.0,
            aqi=75,
            hour=18,
            day_of_week=2
        )
        self.assertIn(t_pred, ["Low", "Moderate", "High", "Critical"])
        self.assertGreaterEqual(t_prob, 0.0)
        self.assertLessEqual(t_prob, 100.0)
        self.assertIsInstance(t_dist, dict)

        f_pred, f_prob, f_dist = prediction_service.predict_flood(
            rainfall=75.0,
            water_level=2.9,
            temperature=24.0,
            humidity=92.0
        )
        self.assertIn(f_pred, ["High", "Critical"])
        print(f"  -> ML OK: Traffic={t_pred} ({t_prob}%), Flood={f_pred} ({f_prob}%)")

    def test_07_risk_and_alerts(self):
        print("\n[Test 7] Testing Risk Engine & Alert Generation...")
        score, label = calculate_location_risk("High", "Low", 70, 0.9, 0.0, congestion_percentage=45.0)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIn(label, ["Low", "Moderate", "High", "Critical"])

        alerts = alert_service.evaluate_and_generate_alerts([{
            "location_id": "central-junction",
            "location_name": "Central Junction",
            "current_speed": 10.0,
            "congestion_percentage": 75.0,
            "delay_seconds": 380,
            "traffic_pred": "Critical",
            "rainfall": 0.0,
            "water_level": 0.8,
            "flood_pred": "Low",
            "aqi": 80,
            "aqi_category": "Moderate"
        }])
        self.assertGreaterEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "Critical")
        self.assertIn("TomTom Traffic", alerts[0]["source"])
        print(f"  -> Risk & Alerts OK: Score={score} ({label}), Alert Generated={alerts[0]['message']}")

    def test_08_data_ingestion_pipeline(self):
        print("\n[Test 8] Testing Complete Data Ingestion Service...")
        telemetry = data_ingestion_service.ingest_data(force_refresh=False)
        self.assertEqual(len(telemetry), 8)
        self.assertEqual(telemetry[0]["traffic_source"], "TomTom Traffic API")
        self.assertEqual(telemetry[0]["weather_source"], "OpenWeather (City-wide)")
        self.assertEqual(telemetry[0]["aqi_source"], "OpenAQ (Coimbatore Station)")
        self.assertEqual(telemetry[0]["water_level_source"], "Hydrological Basin Simulation")

        # Test DEMO MODE toggle
        demo_state = data_ingestion_service.set_mode("DEMO", scenario="heavy_rain")
        self.assertEqual(demo_state["mode"], "DEMO")
        self.assertFalse(demo_state["is_live"])
        demo_telemetry = data_ingestion_service.get_current_telemetry()
        self.assertTrue(demo_telemetry[0]["is_demo"])
        self.assertEqual(demo_telemetry[0]["weather_source"], "Demo Scenario Simulation")

        # Switch back to LIVE MODE
        live_state = data_ingestion_service.set_mode("LIVE")
        self.assertEqual(live_state["mode"], "LIVE")
        self.assertTrue(live_state["is_live"])
        print("  -> Data Ingestion & LIVE/DEMO Mode toggling OK.")

    def test_09_fastapi_endpoints(self):
        print("\n[Test 9] Testing FastAPI REST Endpoints via TestClient...")
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)

        res_root = client.get("/")
        self.assertEqual(res_root.status_code, 200)

        res_status = client.get("/api/city/status")
        self.assertEqual(res_status.status_code, 200)
        status_data = res_status.json()
        self.assertIn("traffic_status", status_data)
        self.assertIn("avg_speed_display", status_data)
        self.assertIn("data_sources", status_data)

        res_locations = client.get("/api/locations")
        self.assertEqual(res_locations.status_code, 200)
        self.assertEqual(len(res_locations.json()), 8)

        res_sources = client.get("/api/data-sources/status")
        self.assertEqual(res_sources.status_code, 200)
        self.assertEqual(len(res_sources.json()), 4)

        res_predict = client.post("/api/predict", json={
            "current_speed": 15.0,
            "free_flow_speed": 40.0,
            "temperature": 29.0,
            "rainfall": 50.0,
            "water_level": 2.2,
            "aqi": 85
        })
        self.assertEqual(res_predict.status_code, 200)
        pred_data = res_predict.json()
        self.assertIn("predicted_traffic_level", pred_data)
        self.assertIn("predicted_flood_risk", pred_data)
        print("  -> FastAPI Endpoints OK: All routes verified.")

if __name__ == "__main__":
    unittest.main()
