# UrbanMind — Smart City Digital Twin

**Subtitle:** API-Integrated Smart City Digital Twin for Multi-Modal Prediction & Proactive Decision Support  
**Project Category:** Final-Year Engineering Project MVP Prototype  
**Configured Target City:** Coimbatore, Tamil Nadu, India (`11.0168° N, 76.9558° E`)

---

> ### 📢 Important Architecture Notice & Project Claim
> **"UrbanMind integrates real external weather, air-quality, and traffic data, while water-level data is currently simulated for the MVP."**  
> Synthetic values for weather, rainfall, temperature, AQI, and traffic flow have been completely replaced with genuine external REST APIs. Water-level telemetry is modelled via an isolated physical basin simulator responding dynamically to real measured precipitation until authorized river radar gauges are integrated.

---

## 1. Executive Summary & Problem Statement

Modern urban centers face interdependent metropolitan challenges: sudden flash flooding from convective rainfall, localized traffic bottlenecks, and deteriorating air quality. Traditional municipal dashboards present isolated historical telemetry without evaluating multi-modal risk correlations or predicting near-future critical horizons.

**UrbanMind** addresses this challenge by establishing an operational Smart City Digital Twin. The system continuously ingests live external environmental, meteorological, and traffic data across 8 strategic urban corridors in Coimbatore. Telemetry feeds into trained **Scikit-Learn Random Forest Machine Learning models** to forecast 30-minute traffic congestion and flood vulnerability horizons with probability distributions. An integrated dynamic risk scoring engine and automated threshold alert pipeline empower city administrators to take proactive mitigation measures before crisis points occur.

---

## 2. Real External Data Sources

UrbanMind connects directly to three industry-standard external REST API providers:

### 1. OpenWeather API
- **Endpoint:** Current Weather Data API (`/data/2.5/weather`)
- **Telemetry Ingested:**
  - Ambient Temperature (°C) & Feels-Like Temperature
  - Precipitation / Rainfall Rate (mm/hour) — safely handling dry intervals as `0.0 mm/h` without random noise
  - Relative Humidity (%)
  - Atmospheric Pressure (hPa)
  - Weather Condition & Description (e.g. *Rain*, *Clear*, *Clouds*)
  - Wind Speed (km/h)
- **Role in Twin:** Drives baseline weather status, flood risk model feature inputs, and hydrological water-level runoff calculation.

### 2. OpenAQ API (v3)
- **Endpoint:** OpenAQ v3 Locations & Sensors API (`/v3/locations/8914/latest`)
- **Station:** Official Tamil Nadu Pollution Control Board (TNPCB) / Central Pollution Control Board (CPCB) Continuous Ambient Air Quality Monitoring Station at **SIDCO Kurichi, Coimbatore**.
- **Telemetry Ingested:**
  - Particulate Matter **PM2.5** (µg/m³)
  - Particulate Matter **PM10** (µg/m³)
  - Nitrogen Dioxide **NO₂** (ppb)
  - Ozone **O₃** (ppb)
  - Carbon Monoxide **CO** (ppb)
  - Sulfur Dioxide **SO₂** (ppb)
- **Documented AQI Calculation:** Computes standard Air Quality Index (0–500) and health categories (*Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Hazardous*) using the official Indian CPCB / US EPA linear breakpoint formula.

### 3. TomTom Traffic Flow API
- **Endpoint:** Flow Segment Data API (`/traffic/services/4/flowSegmentData/absolute/10/json`)
- **Telemetry Ingested (Per Urban Corridor):**
  - **Current Speed:** Real vehicle speed in km/h across the road segment
  - **Free-Flow Speed:** Uncongested reference design speed in km/h
  - **Current Travel Time:** Estimated traversal duration in seconds
  - **Free-Flow Travel Time:** Baseline uncongested traversal duration in seconds
  - **Traffic Delay:** Traversal delay in seconds (`max(0, current_time - free_flow_time)`)
  - **Congestion Percentage:** Calculated as `max(0, (free_flow_speed - current_speed) / free_flow_speed * 100)`
- **Traffic Condition Categorization:**
  - `0% – 20%` → **Low / Normal**
  - `21% – 40%` → **Moderate**
  - `41% – 60%` → **High**
  - `61%+` → **Critical**
- **Note on Vehicle Counts:** TomTom provides speed and travel time metrics rather than discrete vehicle counts; misleading "vehicles/min" labels have been eliminated in favor of real speeds, delays, and congestion percentages.

### 4. Hydrological Water Level Simulation
- **Service Module:** `backend/app/services/water_level_service.py`
- **Specification:** Clearly labeled as `source = "simulation"`.
- **Physical Basin Response:** Rather than generating erratic random numbers, water level starts from a location-specific river/drainage baseline (e.g. 1.4m at River Zone, 0.7m at Central Junction) and dynamically rises in response to real measured rainfall from OpenWeather, gradually draining when rainfall stops.

---

## 3. System Architecture & Data Flow

```
+--------------------------------------------------------------------------------+
|                             EXTERNAL DATA APIS                                 |
|  +--------------------+   +-------------------+   +-------------------------+  |
|  |  OpenWeather API   |   |   OpenAQ v3 API   |   |   TomTom Traffic Flow   |  |
|  |  (Rain/Temp/Hum)   |   |  (PM2.5/PM10/NO2) |   |  (Speed/FreeFlow/Delay) |  |
|  +--------------------+   +-------------------+   +-------------------------+  |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                        FASTAPI DATA INGESTION SERVICE                          |
|  - Rate-limited In-Memory & DB Cache (Weather: 5m, AQI: 5m, Traffic: 2m)       |
|  - Resilient Error Handling (Preserves last valid observation + stale flag)    |
|  - Controlled Water-Level Hydrological Simulator (Rainfall response)           |
|  - Strict Mode Manager: LIVE MODE (Real APIs) vs. DEMO MODE (Scenarios)        |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                         SQLITE TIMESTAMPED DATABASE                            |
|    [ locations | weather_data | air_quality_data | traffic_data | sensor_data ]|
+--------------------------------------------------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
+---------------------------------------+ +--------------------------------------+
|    RANDOM FOREST MACHINE LEARNING     | |         DYNAMIC RISK ENGINE          |
|  - Traffic Model: predict_proba()     | |  - Traffic Risk (40%)                |
|  - Flood Model: predict_proba()       | |  - Flood Risk (40%)                  |
|  - Real feature schema (no fake veh)  | |  - Air Quality Risk (20%)            |
|  - Output: Low / Mod / High / Crit    | |  - Composite Score: 0 – 100          |
+---------------------------------------+ +--------------------------------------+
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                              ALERT ENGINE                                      |
|  Generates threshold alerts: Traffic Congestion, Flood Warning, Poor AQI       |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                             REACT + VITE DASHBOARD                             |
|  - Leaflet OpenStreetMap with real Coimbatore zone pins & telemetry popups     |
|  - KPI Cards (Current Speed, Congestion %, AQI, Rainfall, Flood Risk, Alerts)  |
|  - Data Sources Status Panel (OpenWeather, OpenAQ, TomTom, Simulated Basin)    |
|  - LIVE MODE vs DEMO MODE switch banner                                        |
|  - Recharts Time-Series Historical Analytics                                   |
+--------------------------------------------------------------------------------+
```

---

## 4. Configurable Urban Zones (Coimbatore)

| Zone ID | Location Name | Coordinates | Zone Category | Description |
| :--- | :--- | :--- | :--- | :--- |
| `central-junction` | Central Junction | `11.0183, 76.9644` | Commercial Hub | Gandhipuram cross-cut transit intersection |
| `railway-station` | Railway Station | `10.9984, 76.9632` | Transit Hub | Coimbatore Main Junction Railway Station |
| `airport-road` | Airport Road | `11.0298, 77.0270` | Arterial Corridor | Avinashi Road multi-lane gateway to Airport & IT parks |
| `industrial-area` | Industrial Area | `10.9425, 76.9790` | Industrial Cluster | SIDCO Kurichi industrial cluster by CPCB station |
| `city-hospital` | City Hospital | `10.9995, 76.9702` | Healthcare Corridor | Coimbatore Medical College Hospital (CMCH) |
| `residential-zone` | Residential Zone | `11.0102, 76.9492` | Residential | RS Puram high-density residential & school zone |
| `river-zone` | River Zone | `10.9950, 77.0200` | Flood Prone Basin | Low-lying Noyyal River & Singanallur overflow basin |
| `bus-terminal` | Bus Terminal | `11.0195, 76.9680` | Transit Terminal | Gandhipuram Central & Omni Bus Terminals |

---

## 5. Machine Learning Pipeline

### Real Training vs. Live Prediction
- **Offline Training (`generate_dataset.py` & `train_model.py`):** Trains Random Forest models using realistic historical parameter distributions.
- **Live Online Prediction (`prediction_service.py`):** Operates strictly on live telemetry streamed from OpenWeather, OpenAQ, and TomTom.

### 1. Traffic Congestion Model (`traffic_model.pkl`)
- **Algorithm:** Scikit-Learn `RandomForestClassifier` (`n_estimators=100`, `max_depth=12`)
- **Features (Strictly Real API Inputs):**
  - `current_speed` (TomTom km/h)
  - `free_flow_speed` (TomTom km/h)
  - `congestion_percentage` (Calculated %)
  - `temperature` (OpenWeather °C)
  - `rainfall` (OpenWeather mm/h)
  - `humidity` (OpenWeather %)
  - `aqi` (OpenAQ CPCB AQI)
  - `hour` (Local time)
  - `day_of_week` (Weekday / Weekend)
- **Target:** `Low`, `Moderate`, `High`, `Critical`
- **Probability Output:** Probabilities are extracted using `model.predict_proba()` and presented as **Prediction Probability** rather than unverified confidence.

### 2. Hydrological Flood Risk Model (`flood_model.pkl`)
- **Algorithm:** Scikit-Learn `RandomForestClassifier` (`n_estimators=100`, `max_depth=10`)
- **Features:**
  - `rainfall` (OpenWeather mm/h)
  - `prev_rainfall` (Preceding window mm)
  - `water_level` (Hydrological Basin Simulator m)
  - `temperature` (OpenWeather °C)
  - `humidity` (OpenWeather %)
- **Target:** `Low`, `Moderate`, `High`, `Critical`

---

## 6. Live Mode vs. Demo Mode

To ensure rigorous project evaluations without fabricating live data:
1. **LIVE MODE (Default):**
   - Ingests real OpenWeather, OpenAQ, and TomTom APIs.
   - Map and KPIs reflect current ambient conditions in Coimbatore.
   - Header displays green pulsing indicator: `LIVE DATA`.
2. **DEMO MODE:**
   - Pre-configured controlled scenarios (**Normal**, **Rush Hour**, **Heavy Rain**) allow demonstrating how the Random Forest models, dynamic risk engine, and alert system respond to extreme meteorological or traffic anomalies.
   - When active, a prominent amber banner is displayed:  
     `"DEMO SCENARIO — DATA IS SIMULATED. Controlled scenario active for project evaluation."`
   - A single click on **"Return to LIVE API Mode"** instantly restores live API streaming.

---

## 7. Security & Environment Configuration

API credentials are kept strictly in `backend/.env` and are never exposed to the frontend or committed to source control:

```bash
# backend/.env
OPENWEATHER_API_KEY=your_openweather_key
OPENAQ_API_KEY=your_openaq_key
TOMTOM_API_KEY=your_tomtom_key

CITY_NAME=Coimbatore
LATITUDE=11.0168
LONGITUDE=76.9558

WEATHER_UPDATE_INTERVAL=300
AIR_QUALITY_UPDATE_INTERVAL=300
TRAFFIC_UPDATE_INTERVAL=120
```

- Added `.env`, `*.db`, `*.pkl`, `node_modules/` to `.gitignore`.
- Created `backend/.env.example` with placeholder values for repository distribution.

---

## 8. Installation & Execution Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Step 1: Backend Setup & Testing
```powershell
cd backend

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run automated end-to-end verification test suite
python test_pipeline.py

# Train Random Forest ML models
python train_model.py

# Launch FastAPI Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

### Step 2: Frontend Setup & Launch
Open a separate terminal:
```powershell
cd frontend

# Install frontend dependencies
npm install

# Start Vite React development server
npm run dev
```
*Frontend Dashboard will be accessible at `http://localhost:5173`.*

---

## 9. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/city/status` | Real-time city KPI summary, speed, AQI, rainfall, risk score, and sources |
| `GET` | `/api/locations` | Telemetry, predictions, risk scores, and data source tags for all 8 zones |
| `GET` | `/api/location/{id}` | Detailed telemetry and predictions for a specific location |
| `GET` | `/api/weather` | Latest normalized OpenWeather observation |
| `GET` | `/api/air-quality` | Latest normalized OpenAQ CPCB station observation & calculated AQI |
| `GET` | `/api/traffic` | Latest corridor traffic speeds and congestion rates from TomTom |
| `GET` | `/api/predictions` | Random Forest predictions with `predict_proba` distributions |
| `GET` | `/api/alerts` | Active threshold alerts with severity, message, and source attribution |
| `GET` | `/api/analytics` | Timestamped historical observations from SQLite for time-series charts |
| `GET` | `/api/data-sources/status` | Connection status for OpenWeather, OpenAQ, TomTom, and Water Level |
| `POST` | `/api/simulate` | Toggles LIVE MODE or activates controlled DEMO scenarios |
| `POST` | `/api/predict` | On-demand custom prediction endpoint for manual evaluation testing |

---

## 10. College Review Demonstration Script

1. **Verify Live Data Ingestion:**
   - Open `http://localhost:5173/`. Point to the header pill showing `LIVE DATA — Coimbatore, India`.
   - Direct attention to the **Data Sources Panel**:
     - *OpenWeather:* Connected (City-wide)
     - *OpenAQ:* Connected (SIDCO Kurichi Station)
     - *TomTom:* Connected (Corridor flow)
     - *Water Level:* Simulated (Rainfall-driven)
2. **Review Real KPIs:**
   - Inspect the KPI cards: real Traffic Speed (e.g. 23 km/h), Congestion %, CPCB AQI (e.g. 78 Moderate), Rainfall rate (mm/h), and Flood Risk.
3. **Inspect Zone Telemetry:**
   - Click a marker on the Leaflet map (e.g. Central Junction or Industrial Area).
   - In the inspector modal, demonstrate real TomTom current speed, free-flow speed, and delay.
   - Note the explicit source attribution for every single parameter.
4. **Demonstrate Machine Learning Predict Proba:**
   - Show the Random Forest predictions indicating 30-minute horizons with genuine probability percentages.
5. **Demonstrate Demo Scenarios:**
   - Click **[ Rush Hour ]**: Observe speed dropping, congestion % surging, and AI traffic prediction escalating to High/Critical.
   - Click **[ Heavy Rain ]**: Observe rainfall surging, simulated water level rising in response, and flood prediction escalating to Critical with active alerts triggered.
6. **Return to Live Mode:**
   - Click **"Return to LIVE API Mode"** to demonstrate seamless reversion to live external API streaming.
7. **Explain Architectural Honesty:**
   - Emphasize adherence to scientific integrity: water level is simulated because authorized river gauges require municipal clearance, while weather, AQI, and traffic are 100% genuine real-time external APIs.
