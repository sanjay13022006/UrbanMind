# Urban Mind — Smart City Digital Twin

**Subtitle:** AI-Powered Smart City Digital Twin for Prediction and Decision Support  
**Project Category:** Final-Year College Project MVP Prototype  

---

## 1. Executive Summary & Problem Statement

Modern urban centers face complex challenges including unpredictable traffic congestion, air pollution, and rapid flash flooding. Traditional smart city monitoring systems rely on static dashboards that display past telemetry without forecasting near-future risks or providing proactive decision support.

**Urban Mind** bridges this gap by creating a virtual representation (Digital Twin) of a smart city. The system processes live/simulated sensor streams across multiple city zones, evaluates real-time environmental metrics, and executes trained **Random Forest Machine Learning models** to predict 30-minute traffic congestion and flood risk horizons. An integrated dynamic risk scoring engine and threshold-based alert system empower city managers to intervene before critical incidents occur.

---

## 2. Key Project Objectives

- **Functional Virtual Twin:** Maintain real-time telemetry models for 8 distinct urban zones (Central Junction, Railway Station, Airport Road, Industrial Area, City Hospital, Residential Zone, River Zone, Bus Terminal).
- **ML-Driven Predictions:** Train and deploy real Machine Learning prediction models (Traffic Congestion & Flood Risk) using Python and Scikit-learn.
- **Dynamic Risk & Alert Engine:** Calculate real-time composite risk scores (0–100) and generate automated threshold alerts for traffic, air quality, and flooding.
- **Interactive Geospatial Visualization:** Render an OpenStreetMap-powered Leaflet dashboard with status-colored zone markers and interactive telemetry popups.
- **Review Panel Demo Suite:** Provide preset simulation scenarios (**Normal**, **Rush Hour**, **Heavy Rain**) and a "Run Simulation" trigger button to demonstrate live twin reactions during evaluation.

---

## 3. System Architecture & Flow

```
+------------------------+
|    Sensor Simulator    |  --> (Smooth variations or Scenario trigger)
+------------------------+
            |
            v
+------------------------+
|   FastAPI REST API     |  <-->  [ SQLite Database: city.db ]
+------------------------+
            |
            +--->  [ Traffic Random Forest Model (.pkl) ]
            +--->  [ Flood Risk Random Forest Model (.pkl) ]
            |
            v
+------------------------+
| Dynamic Risk & Alerts  |  -->  (Composite Risk Score & Threshold Alerts)
+------------------------+
            |
            v
+------------------------+
| React + Vite Dashboard |  -->  (Leaflet Map + KPI Cards + Recharts Analytics)
+------------------------+
```

---

## 4. Technology Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic, SQLite
- **Machine Learning:** Scikit-learn (Random Forest Classifier), Pandas, NumPy, Joblib
- **Frontend:** React 18, Vite, Leaflet.js, React-Leaflet, Recharts, Lucide React, Axios
- **Design System:** Minimalist Professional Theme (White background `#FFFFFF`, Light Gray sections `#F8FAFC`, Status Accents Green/Yellow/Red/Blue, Crisp Typography)

---

## 5. Machine Learning Models & Dataset Generation

### Synthetic Dataset (`generate_dataset.py`)
Generates 8,000 realistic historical sensor records containing:
- `timestamp`, `location`, `vehicle_count`, `traffic_speed`, `aqi`, `temperature`, `rainfall`, `prev_rainfall`, `water_level`, `hour`, `day_of_week`.
- Incorporates domain-specific correlations: peak rush hours drop traffic speeds; industrial zones elevate baseline AQI; river zones elevate water levels; heavy rainfall reduces speed and increases flood probability.

### Trained Models (`train_model.py`)
1. **Traffic Congestion Model (`traffic_model.pkl`):**
   - **Algorithm:** Random Forest Classifier (`n_estimators=100`, `max_depth=12`)
   - **Features:** `[vehicle_count, traffic_speed, hour, day_of_week, aqi, temperature, rainfall]`
   - **Target:** Traffic Congestion Level (`Low`, `Moderate`, `High`, `Critical`)
   - **Accuracy:** ~98.8%
2. **Flood Risk Model (`flood_model.pkl`):**
   - **Algorithm:** Random Forest Classifier (`n_estimators=100`, `max_depth=10`)
   - **Features:** `[rainfall, water_level, temperature, prev_rainfall]`
   - **Target:** Flood Risk Level (`Low`, `Moderate`, `High`, `Critical`)
   - **Accuracy:** ~99.6%

*Confidence scores displayed on the dashboard are extracted directly from the model's prediction probabilities (`predict_proba`).*

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.9+ installed
- Node.js v18+ installed

### Step 1: Set Up Backend & Train ML Models
```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip install -r requirements.txt

# Generate synthetic dataset (creates data/dataset.csv)
python generate_dataset.py

# Train ML models (saves models/traffic_model.pkl & flood_model.pkl)
python train_model.py

# Launch FastAPI Backend Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API will be live at: `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).*

### Step 2: Set Up Frontend & Launch Dashboard
Open a new terminal window:
```bash
# Navigate to frontend folder
cd frontend

# Install node packages
npm install

# Launch Vite React Dev Server
npm run dev
```
*Frontend Dashboard will be live at: `http://localhost:5173`.*

---

## 7. API Reference Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/city/status` | Returns summary KPIs, overall risk score, and system health |
| `GET` | `/api/locations` | Returns list of 8 city zones with telemetry, risk scores, and status colors |
| `GET` | `/api/location/{id}` | Returns telemetry and predictions for a specific location ID |
| `GET` | `/api/sensors` | Returns latest raw sensor snapshots |
| `GET` | `/api/predictions` | Returns live AI traffic & flood predictions with confidence % |
| `GET` | `/api/alerts` | Returns active threshold alerts sorted by severity |
| `GET` | `/api/analytics` | Returns historical time-series data for trend charts |
| `POST` | `/api/simulate` | Triggers a simulation step or sets scenario (`normal`, `rush_hour`, `heavy_rain`) |
| `POST` | `/api/predict` | Executes custom on-demand prediction for manual inputs |

---

## 8. Step-by-Step College Review Demonstration Script

During your project evaluation, follow this 10-step sequence:

1. **Open Dashboard:** Navigate to `http://localhost:5173/`. Point out the header title **Urban Mind** and "Online" system status.
2. **Interactive City Map:** Show the Leaflet map containing 8 markers (Central Junction, Railway Station, Airport Road, River Zone, etc.) with color-coded status pins.
3. **Location Telemetry:** Click a map marker (e.g. Central Junction) to open the Location Inspector modal showing vehicle count, speed, AQI, temp, rain, water level, risk score, and ML predictions.
4. **Current Status KPIs:** Review the top KPI cards showing city average traffic volume, AQI category, flood risk, active alerts, and overall risk score (e.g. 42 / 100 Moderate).
5. **Scenario 1 - Rush Hour Simulation:** Click **[ Rush Hour ]** in the Scenario Selector bar.
   - Observe immediate vehicle count increase to >150 veh/min and traffic speed drop to <15 km/h.
   - Point to the AI Prediction panel forecasting **Critical Traffic Congestion** with high confidence.
6. **Scenario 2 - Heavy Rain Simulation:** Click **[ Heavy Rain ]** in the Scenario Selector bar.
   - Observe rainfall spiking (>90mm) and water level rising (>3.5m) at River Zone.
   - Point to the AI Prediction panel updating Flood Risk to **Critical** and AQI dropping to Good (rain washing pollutants).
7. **Active Alert Engine:** Scroll to the Active Alerts section to demonstrate dynamically generated alerts ("Potential flooding warning near River Zone", "High traffic congestion detected").
8. **Historical Trend Charts:** Scroll to the Analytics section to demonstrate live time-series charts (Traffic volume, AQI index, City Risk score) updating every 5 seconds.
9. **Reset Scenario:** Click **[ Normal ]** to restore baseline city conditions.
10. **Future Scope Explanation:** Highlight the roadmap panel explaining future expansion vectors (IoT hardware integration, 3D Mesh twin, Satellite flood mapping, AI adaptive traffic signal control).

---

## 9. Future Development Roadmap

1. **Real IoT Hardware Integration:** Edge microcontrollers with MQTT data streaming.
2. **Real-Time CCTV Analysis:** OpenCV vehicle counting and optical speed tracking.
3. **3D City Mesh Twin:** Three.js / Cesium web GL geospatial rendering.
4. **Satellite Imagery:** Copernicus Sentinel radar data for regional flood boundary detection.
5. **Autonomous Signal Control:** AI adaptive traffic light duration optimization.

---

## 10. Project Team & Responsibilities

- **Student Name / Reg No:** Final Year B.Tech Project
- **Domain:** Artificial Intelligence & Smart City Infrastructure
- **Guide / Supervisor:** Project Review Committee
