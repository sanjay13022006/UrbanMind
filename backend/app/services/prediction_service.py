import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TRAFFIC_MODEL_PATH = BASE_DIR / "models" / "traffic_model.pkl"
FLOOD_MODEL_PATH = BASE_DIR / "models" / "flood_model.pkl"

class PredictionService:
    def __init__(self):
        self.traffic_data = None
        self.flood_data = None
        self._load_models()

    def _load_models(self):
        if TRAFFIC_MODEL_PATH.exists():
            try:
                self.traffic_data = joblib.load(TRAFFIC_MODEL_PATH)
            except Exception as e:
                print(f"Error loading traffic model: {e}")
        
        if FLOOD_MODEL_PATH.exists():
            try:
                self.flood_data = joblib.load(FLOOD_MODEL_PATH)
            except Exception as e:
                print(f"Error loading flood model: {e}")

    def predict_traffic(self, vehicle_count, traffic_speed, hour, day_of_week, aqi, temperature, rainfall):
        if not self.traffic_data:
            # Fallback heuristic if model not loaded
            if vehicle_count > 150 or traffic_speed < 15:
                return "Critical", 85.0
            elif vehicle_count > 100 or traffic_speed < 25:
                return "High", 80.0
            elif vehicle_count > 60:
                return "Moderate", 75.0
            return "Low", 90.0

        model = self.traffic_data["model"]
        features = self.traffic_data["features"]
        
        input_df = pd.DataFrame([{
            "vehicle_count": vehicle_count,
            "traffic_speed": traffic_speed,
            "hour": hour,
            "day_of_week": day_of_week,
            "aqi": aqi,
            "temperature": temperature,
            "rainfall": rainfall
        }])[features]
        
        pred_class = model.predict(input_df)[0]
        probs = model.predict_proba(input_df)[0]
        max_prob = float(np.max(probs)) * 100.0
        
        return pred_class, round(max_prob, 1)

    def predict_flood(self, rainfall, water_level, temperature, prev_rainfall=0.0):
        if not self.flood_data:
            if rainfall > 80 or water_level > 3.0:
                return "Critical", 88.0
            elif rainfall > 40 or water_level > 2.0:
                return "High", 82.0
            elif rainfall > 15 or water_level > 1.2:
                return "Moderate", 78.0
            return "Low", 92.0

        model = self.flood_data["model"]
        features = self.flood_data["features"]
        
        input_df = pd.DataFrame([{
            "rainfall": rainfall,
            "water_level": water_level,
            "temperature": temperature,
            "prev_rainfall": prev_rainfall
        }])[features]
        
        pred_class = model.predict(input_df)[0]
        probs = model.predict_proba(input_df)[0]
        max_prob = float(np.max(probs)) * 100.0
        
        return pred_class, round(max_prob, 1)

prediction_service = PredictionService()
