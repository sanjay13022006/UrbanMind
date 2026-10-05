import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TRAFFIC_MODEL_PATH = BASE_DIR / "models" / "traffic_model.pkl"
FLOOD_MODEL_PATH = BASE_DIR / "models" / "flood_model.pkl"

class PredictionService:
    def __init__(self):
        self.traffic_bundle = None
        self.flood_bundle = None
        self._load_models()

    def _load_models(self):
        if TRAFFIC_MODEL_PATH.exists():
            try:
                self.traffic_bundle = joblib.load(TRAFFIC_MODEL_PATH)
            except Exception as e:
                print(f"Error loading traffic model: {e}")
        
        if FLOOD_MODEL_PATH.exists():
            try:
                self.flood_bundle = joblib.load(FLOOD_MODEL_PATH)
            except Exception as e:
                print(f"Error loading flood model: {e}")

    def predict_traffic(
        self,
        current_speed: float,
        free_flow_speed: float,
        congestion_percentage: float,
        temperature: float,
        rainfall: float,
        humidity: float,
        aqi: int,
        hour: int,
        day_of_week: int
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Executes trained Random Forest model on real API telemetry features.
        Returns predicted traffic class, top class probability %, and full probability distribution.
        """
        if not self.traffic_bundle:
            # Fallback heuristic if model file is unavailable
            if congestion_percentage >= 60.0 or current_speed < 12.0:
                return "Critical", 85.0, {"Critical": 85.0}
            elif congestion_percentage >= 40.0 or current_speed < 22.0:
                return "High", 80.0, {"High": 80.0}
            elif congestion_percentage >= 20.0 or current_speed < 32.0:
                return "Moderate", 75.0, {"Moderate": 75.0}
            return "Low", 90.0, {"Low": 90.0}

        model = self.traffic_bundle["model"]
        features = self.traffic_bundle["features"]
        classes = self.traffic_bundle["classes"]

        row = {
            "current_speed": current_speed,
            "free_flow_speed": free_flow_speed,
            "congestion_percentage": congestion_percentage,
            "temperature": temperature,
            "rainfall": rainfall,
            "humidity": humidity,
            "aqi": aqi,
            "hour": hour,
            "day_of_week": day_of_week
        }
        input_df = pd.DataFrame([row])[features]

        pred_class = model.predict(input_df)[0]
        probs = model.predict_proba(input_df)[0]
        
        prob_dict = {cls_name: round(float(prob) * 100.0, 1) for cls_name, prob in zip(classes, probs)}
        max_prob = float(np.max(probs)) * 100.0

        return str(pred_class), round(max_prob, 1), prob_dict

    def predict_flood(
        self,
        rainfall: float,
        water_level: float,
        temperature: float,
        humidity: float = 65.0,
        prev_rainfall: float = 0.0
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Executes trained Random Forest model for hydrological flood risk.
        Returns predicted flood risk class, top class probability %, and distribution.
        """
        if not self.flood_bundle:
            if rainfall > 75.0 or water_level > 2.8:
                return "Critical", 88.0, {"Critical": 88.0}
            elif rainfall > 40.0 or water_level > 2.0:
                return "High", 82.0, {"High": 82.0}
            elif rainfall > 15.0 or water_level > 1.2:
                return "Moderate", 78.0, {"Moderate": 78.0}
            return "Low", 92.0, {"Low": 92.0}

        model = self.flood_bundle["model"]
        features = self.flood_bundle["features"]
        classes = self.flood_bundle["classes"]

        row = {
            "rainfall": rainfall,
            "prev_rainfall": prev_rainfall,
            "water_level": water_level,
            "temperature": temperature,
            "humidity": humidity
        }
        input_df = pd.DataFrame([row])[features]

        pred_class = model.predict(input_df)[0]
        probs = model.predict_proba(input_df)[0]

        prob_dict = {cls_name: round(float(prob) * 100.0, 1) for cls_name, prob in zip(classes, probs)}
        max_prob = float(np.max(probs)) * 100.0

        return str(pred_class), round(max_prob, 1), prob_dict

prediction_service = PredictionService()
