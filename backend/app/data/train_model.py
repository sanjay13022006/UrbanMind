import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_DIR = BASE_DIR / "models"

def train_and_save_models():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    if not DATA_PATH.exists():
        print("Dataset not found. Generating new dataset...")
        from app.data.generate_dataset import generate_synthetic_dataset
        df = generate_synthetic_dataset()
    else:
        df = pd.read_csv(DATA_PATH)
        
    print(f"Loaded dataset with {len(df)} records for ML training.")
    
    # Target label mapping
    LABEL_ORDER = ["Low", "Moderate", "High", "Critical"]
    
    # ----------------------------------------------------
    # 1. TRAFFIC CONGESTION PREDICTION MODEL
    # ----------------------------------------------------
    print("\n--- Training Traffic Congestion Prediction Model (Random Forest) ---")
    traffic_features = ["vehicle_count", "traffic_speed", "hour", "day_of_week", "aqi", "temperature", "rainfall"]
    X_traffic = df[traffic_features]
    y_traffic = df["traffic_level"]
    
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_traffic, y_traffic, test_size=0.2, random_state=42, stratify=y_traffic
    )
    
    traffic_rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    traffic_rf.fit(X_train_t, y_train_t)
    
    y_pred_t = traffic_rf.predict(X_test_t)
    acc_t = accuracy_score(y_test_t, y_pred_t)
    prec_t, rec_t, f1_t, _ = precision_recall_fscore_support(y_test_t, y_pred_t, average="macro")
    
    print(f"Traffic Model Evaluation Metrics:")
    print(f"  Accuracy:  {acc_t * 100:.2f}%")
    print(f"  Precision: {prec_t * 100:.2f}%")
    print(f"  Recall:    {rec_t * 100:.2f}%")
    print(f"  F1 Score:  {f1_t * 100:.2f}%")
    
    traffic_model_path = MODEL_DIR / "traffic_model.pkl"
    joblib.dump({
        "model": traffic_rf,
        "features": traffic_features,
        "classes": traffic_rf.classes_.tolist()
    }, traffic_model_path)
    print(f"Saved Traffic Model to: {traffic_model_path}")

    # ----------------------------------------------------
    # 2. FLOOD RISK PREDICTION MODEL
    # ----------------------------------------------------
    print("\n--- Training Flood Risk Prediction Model (Random Forest) ---")
    flood_features = ["rainfall", "water_level", "temperature", "prev_rainfall"]
    X_flood = df[flood_features]
    y_flood = df["flood_risk"]
    
    X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
        X_flood, y_flood, test_size=0.2, random_state=42, stratify=y_flood
    )
    
    flood_rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    flood_rf.fit(X_train_f, y_train_f)
    
    y_pred_f = flood_rf.predict(X_test_f)
    acc_f = accuracy_score(y_test_f, y_pred_f)
    prec_f, rec_f, f1_f, _ = precision_recall_fscore_support(y_test_f, y_pred_f, average="macro")
    
    print(f"Flood Model Evaluation Metrics:")
    print(f"  Accuracy:  {acc_f * 100:.2f}%")
    print(f"  Precision: {prec_f * 100:.2f}%")
    print(f"  Recall:    {rec_f * 100:.2f}%")
    print(f"  F1 Score:  {f1_f * 100:.2f}%")
    
    flood_model_path = MODEL_DIR / "flood_model.pkl"
    joblib.dump({
        "model": flood_rf,
        "features": flood_features,
        "classes": flood_rf.classes_.tolist()
    }, flood_model_path)
    print(f"Saved Flood Model to: {flood_model_path}")
    print("\nML Training completed successfully.")

if __name__ == "__main__":
    train_and_save_models()
