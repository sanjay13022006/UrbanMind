"""
Random Forest Model Training and Evaluation Pipeline (30-Minute Forward Horizon)
--------------------------------------------------------------------------------
Trains separate Random Forest classifiers for:
1. Traffic Congestion State (30m Horizon): ['Low', 'Moderate', 'High', 'Critical']
2. Flood Risk State (30m Horizon):        ['Low', 'Moderate', 'High', 'Critical']

Validates using stratified train/test split (80/20) and computes:
- Accuracy, Precision, Recall, F1-Score (macro and weighted)
- Full Confusion Matrices
- Out-of-sample probability calibration diagnostics
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support
)
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_DIR = BASE_DIR / "models"

def train_and_save_models():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("URBANMIND ML PIPELINE: 30-MINUTE HORIZON MODEL TRAINING")
    print("=" * 70)
    
    from app.data.generate_dataset import generate_training_dataset
    print("Generating synthetic 30-minute forward horizon training dataset...")
    df = generate_training_dataset(num_records=12000, output_path=DATA_PATH)
    print(f"Loaded dataset with {len(df)} records.\n")
    
    # --------------------------------------------------------------------
    # 1. TRAFFIC CONGESTION PREDICTION MODEL (30-Minute Forward Horizon)
    # --------------------------------------------------------------------
    print("-" * 70)
    print("1. TRAINING TRAFFIC CONGESTION MODEL (30m Horizon)")
    print("-" * 70)
    traffic_features = [
        "current_speed",
        "free_flow_speed",
        "congestion_percentage",
        "temperature",
        "rainfall",
        "humidity",
        "aqi",
        "hour",
        "day_of_week"
    ]
    X_traffic = df[traffic_features]
    y_traffic = df["traffic_level"]
    
    print("Traffic Target Distribution:")
    for cls_name, count in y_traffic.value_counts().items():
        print(f"  - {cls_name:10s}: {count:5d} ({count / len(y_traffic) * 100:.1f}%)")
        
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_traffic, y_traffic, test_size=0.20, random_state=42, stratify=y_traffic
    )
    
    # Regularized Random Forest avoiding overfitted single-sample pure leaves
    traffic_rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=12,
        min_samples_leaf=5,
        random_state=42
    )
    traffic_rf.fit(X_train_t, y_train_t)
    
    y_pred_t = traffic_rf.predict(X_test_t)
    probs_t = traffic_rf.predict_proba(X_test_t)
    max_probs_t = np.max(probs_t, axis=1) * 100.0
    
    acc_t = accuracy_score(y_test_t, y_pred_t)
    prec_m_t, rec_m_t, f1_m_t, _ = precision_recall_fscore_support(y_test_t, y_pred_t, average="macro")
    prec_w_t, rec_w_t, f1_w_t, _ = precision_recall_fscore_support(y_test_t, y_pred_t, average="weighted")
    
    print(f"\nTraffic Model Metrics (Test Set n={len(y_test_t)}):")
    print(f"  Accuracy:         {acc_t * 100:.2f}%")
    print(f"  Macro Precision:  {prec_m_t * 100:.2f}%")
    print(f"  Macro Recall:     {rec_m_t * 100:.2f}%")
    print(f"  Macro F1-Score:   {f1_m_t * 100:.2f}%")
    print(f"  Weighted F1:      {f1_w_t * 100:.2f}%")
    print(f"  Probability Range: Min={max_probs_t.min():.1f}%, Mean={max_probs_t.mean():.1f}%, Median={np.median(max_probs_t):.1f}%, Max={max_probs_t.max():.1f}%")
    
    cm_t = confusion_matrix(y_test_t, y_pred_t, labels=traffic_rf.classes_)
    print("\nConfusion Matrix (Classes: {}):".format(traffic_rf.classes_.tolist()))
    print(cm_t)
    
    print("\nDetailed Classification Report:")
    print(classification_report(y_test_t, y_pred_t, digits=3))
    
    traffic_model_path = MODEL_DIR / "traffic_model.pkl"
    joblib.dump({
        "model": traffic_rf,
        "features": traffic_features,
        "classes": traffic_rf.classes_.tolist(),
        "horizon": "30 minutes"
    }, traffic_model_path)
    print(f"Saved Traffic Model bundle to: {traffic_model_path}\n")

    # --------------------------------------------------------------------
    # 2. FLOOD RISK PREDICTION MODEL (30-Minute Forward Horizon)
    # --------------------------------------------------------------------
    print("-" * 70)
    print("2. TRAINING FLOOD RISK MODEL (30m Horizon)")
    print("-" * 70)
    flood_features = ["rainfall", "prev_rainfall", "water_level", "temperature", "humidity"]
    X_flood = df[flood_features]
    y_flood = df["flood_risk"]
    
    print("Flood Target Distribution:")
    for cls_name, count in y_flood.value_counts().items():
        print(f"  - {cls_name:10s}: {count:5d} ({count / len(y_flood) * 100:.1f}%)")
        
    X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
        X_flood, y_flood, test_size=0.20, random_state=42, stratify=y_flood
    )
    
    flood_rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=12,
        min_samples_leaf=5,
        random_state=42
    )
    flood_rf.fit(X_train_f, y_train_f)
    
    y_pred_f = flood_rf.predict(X_test_f)
    probs_f = flood_rf.predict_proba(X_test_f)
    max_probs_f = np.max(probs_f, axis=1) * 100.0
    
    acc_f = accuracy_score(y_test_f, y_pred_f)
    prec_m_f, rec_m_f, f1_m_f, _ = precision_recall_fscore_support(y_test_f, y_pred_f, average="macro")
    prec_w_f, rec_w_f, f1_w_f, _ = precision_recall_fscore_support(y_test_f, y_pred_f, average="weighted")
    
    print(f"\nFlood Model Metrics (Test Set n={len(y_test_f)}):")
    print(f"  Accuracy:         {acc_f * 100:.2f}%")
    print(f"  Macro Precision:  {prec_m_f * 100:.2f}%")
    print(f"  Macro Recall:     {rec_m_f * 100:.2f}%")
    print(f"  Macro F1-Score:   {f1_m_f * 100:.2f}%")
    print(f"  Weighted F1:      {f1_w_f * 100:.2f}%")
    print(f"  Probability Range: Min={max_probs_f.min():.1f}%, Mean={max_probs_f.mean():.1f}%, Median={np.median(max_probs_f):.1f}%, Max={max_probs_f.max():.1f}%")
    
    cm_f = confusion_matrix(y_test_f, y_pred_f, labels=flood_rf.classes_)
    print("\nConfusion Matrix (Classes: {}):".format(flood_rf.classes_.tolist()))
    print(cm_f)
    
    print("\nDetailed Classification Report:")
    print(classification_report(y_test_f, y_pred_f, digits=3))
    
    flood_model_path = MODEL_DIR / "flood_model.pkl"
    joblib.dump({
        "model": flood_rf,
        "features": flood_features,
        "classes": flood_rf.classes_.tolist(),
        "horizon": "30 minutes"
    }, flood_model_path)
    print(f"Saved Flood Model bundle to: {flood_model_path}")
    print("\n" + "=" * 70)
    print("ALL RANDOM FOREST MODELS SUCCESSFULLY TRAINED & EVALUATED")
    print("=" * 70)

if __name__ == "__main__":
    train_and_save_models()
