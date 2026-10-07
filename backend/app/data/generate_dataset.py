"""
Synthetic Urban Telemetry Dataset Generator (30-Minute Forward Horizon)
----------------------------------------------------------------------
Generates realistic historical time-series telemetry for offline ML model training.
Features reflect observable inputs at time t from real APIs:
- TomTom: current_speed, free_flow_speed, congestion_percentage
- OpenWeather: temperature, rainfall, humidity
- OpenAQ: aqi
- Controlled Hydrology: water_level, prev_rainfall
- Time: hour, day_of_week

Targets (y) reflect conditions 30 MINUTES INTO THE FUTURE (t + 30 min):
- traffic_level (30m future traffic severity: Low, Moderate, High, Critical)
- flood_risk   (30m future hydrological risk: Low, Moderate, High, Critical)

METHODOLOGY NOTE:
The dataset is synthetic. To eliminate direct target leakage and trivial 100%
classification, the target is NOT generated from exact same-instant feature thresholds.
Instead, physical process dynamics (diurnal demand shifts, weather friction, drainage,
and realistic urban stochastic variance) transition the state forward 30 minutes.
Observable features at time t predict the conditional probability distribution at t + 30m.
"""

import datetime
from pathlib import Path
import numpy as np
import pandas as pd

LOCATIONS = [
    "central-junction",
    "railway-station",
    "airport-road",
    "industrial-area",
    "city-hospital",
    "residential-zone",
    "river-zone",
    "bus-terminal"
]

def generate_training_dataset(num_records=12000, output_path=None, random_seed=42):
    """
    Simulates multi-week time-series sequences of urban telemetry per location.
    Extracts observable features at step t and targets at step t + 2 (30 minutes ahead).
    """
    np.random.seed(random_seed)
    start_date = datetime.datetime(2026, 6, 1, 0, 0, 0)
    
    records = []
    steps_ahead = 2  # 2 x 15min steps = 30-minute forward prediction horizon
    time_steps = (num_records // len(LOCATIONS)) + steps_ahead + 25

    for loc in LOCATIONS:
        # Corridor-specific physical characteristics
        if loc in ["airport-road"]:
            free_flow_speed = 55.0
            corridor_bottleneck = 0.85
        elif loc in ["central-junction", "bus-terminal", "railway-station"]:
            free_flow_speed = 36.0
            corridor_bottleneck = 1.25
        elif loc in ["industrial-area"]:
            free_flow_speed = 42.0
            corridor_bottleneck = 1.10
        else:
            free_flow_speed = 44.0
            corridor_bottleneck = 0.95
            
        loc_water_vulnerability = 1.35 if loc == "river-zone" else 0.85
        loc_aqi_bias = 1.35 if loc == "industrial-area" else 1.0
        base_water_level = 0.75 if loc == "river-zone" else 0.50
        
        cur_rainfall = 0.0
        cur_water_level = base_water_level
        weather_regime = 0  # 0: dry/clear (75%), 1: scattered showers (18%), 2: monsoon downpour (7%)
        regime_duration = 0
        
        loc_history = []
        
        for t in range(time_steps):
            dt = start_date + datetime.timedelta(minutes=t * 15)
            hour = dt.hour
            day_of_week = dt.weekday()
            is_weekday = day_of_week < 5
            
            # Weather regime management: days are predominantly dry with episodic rain
            regime_duration += 1
            if regime_duration > 16:  # at least 4 hours per regime
                r_trans = np.random.rand()
                if weather_regime == 0 and r_trans < 0.06:
                    weather_regime = 1 if np.random.rand() < 0.80 else 2
                    regime_duration = 0
                elif weather_regime == 1 and r_trans < 0.25:
                    weather_regime = 0 if np.random.rand() < 0.85 else 2
                    regime_duration = 0
                elif weather_regime == 2 and r_trans < 0.40:
                    weather_regime = 1 if np.random.rand() < 0.60 else 0
                    regime_duration = 0
                    
            if weather_regime == 0:
                rainfall = 0.0 if np.random.rand() < 0.97 else np.random.uniform(0.1, 1.2)
            elif weather_regime == 1:
                rainfall = np.random.uniform(4.0, 25.0)
            else:
                rainfall = np.random.uniform(30.0, 85.0)
                
            prev_rainfall = cur_rainfall
            cur_rainfall = rainfall
            
            temperature = round(float(np.random.uniform(24.0, 35.0) - (rainfall * 0.06)), 1)
            humidity = round(float(np.clip(54.0 + (rainfall * 0.40) + np.random.normal(0, 4), 38.0, 98.0)), 1)
            
            # Hydrological physical response with natural drainage
            inflow = (rainfall * 0.020 * loc_water_vulnerability) + (prev_rainfall * 0.007)
            drainage = 0.16 * max(0.0, cur_water_level - base_water_level)
            cur_water_level = max(0.35, cur_water_level + inflow - drainage + np.random.normal(0, 0.015))
            cur_water_level = min(3.8, cur_water_level)
            water_level = round(float(cur_water_level), 2)
            
            # Diurnal base traffic demand curve
            if is_weekday:
                if 8 <= hour <= 10:
                    rush_phase = (hour - 8) + (dt.minute / 60.0)
                    base_factor = 0.55 + 0.30 * np.sin(rush_phase / 2.0 * np.pi)
                elif 17 <= hour <= 20:
                    rush_phase = (hour - 17) + (dt.minute / 60.0)
                    base_factor = 0.50 + 0.35 * np.sin(rush_phase / 3.0 * np.pi)
                elif 11 <= hour <= 16:
                    base_factor = 0.30 + 0.15 * np.random.uniform(0, 1)
                else:
                    base_factor = 0.08 + 0.12 * np.random.uniform(0, 1)
            else:
                if 12 <= hour <= 20:
                    base_factor = 0.30 + 0.25 * np.random.uniform(0, 1)
                else:
                    base_factor = 0.08 + 0.12 * np.random.uniform(0, 1)
                    
            congestion_factor = base_factor * corridor_bottleneck
            
            # Weather friction
            if rainfall > 25.0:
                congestion_factor += min(0.25, rainfall * 0.003)
            elif rainfall > 5.0:
                congestion_factor += 0.08
                
            congestion_factor = np.clip(congestion_factor + np.random.normal(0, 0.035), 0.05, 0.95)
            
            current_speed = round(float(free_flow_speed * (1.0 - congestion_factor) + np.random.normal(0, 1.0)), 1)
            current_speed = max(5.0, min(free_flow_speed, current_speed))
            congestion_pct = round(max(0.0, (free_flow_speed - current_speed) / free_flow_speed * 100.0), 1)
            
            # AQI
            aqi_traffic = congestion_pct * 0.40
            aqi_rain = rainfall * 0.45
            aqi = int(np.clip(45 * loc_aqi_bias + aqi_traffic - aqi_rain + np.random.normal(0, 6), 22, 230))
            
            loc_history.append({
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "location": loc,
                "current_speed": current_speed,
                "free_flow_speed": free_flow_speed,
                "congestion_percentage": congestion_pct,
                "temperature": temperature,
                "rainfall": rainfall,
                "humidity": humidity,
                "prev_rainfall": prev_rainfall,
                "water_level": water_level,
                "aqi": aqi,
                "hour": hour,
                "day_of_week": day_of_week,
                "cong_factor": congestion_factor,
                "water_val": water_level,
                "rain_val": rainfall
            })
            
        # Target assignment 30 minutes (2 steps) into future
        for t in range(len(loc_history) - steps_ahead):
            cur = loc_history[t]
            fut = loc_history[t + steps_ahead]
            
            # Future traffic class after 30 minutes
            fut_cong = fut["cong_factor"] * 100.0
            fut_spd = fut["current_speed"]
            
            if fut_cong >= 62.0 or fut_spd < 14.0:
                traffic_target = "Critical"
            elif fut_cong >= 42.0 or fut_spd < 23.0:
                traffic_target = "High"
            elif fut_cong >= 22.0 or fut_spd < 33.0:
                traffic_target = "Moderate"
            else:
                traffic_target = "Low"
                
            # Future flood class after 30 minutes
            fut_w = fut["water_val"]
            fut_r = fut["rain_val"]
            flood_index = (fut_r * 0.40) + (fut_w * 22.0)
            
            if fut_w >= 2.2 or (fut_r >= 55.0 and fut_w >= 1.6) or flood_index >= 65.0:
                flood_target = "Critical"
            elif fut_w >= 1.5 or (fut_r >= 30.0 and fut_w >= 1.1) or flood_index >= 42.0:
                flood_target = "High"
            elif fut_w >= 0.95 or fut_r >= 10.0 or flood_index >= 20.0:
                flood_target = "Moderate"
            else:
                flood_target = "Low"
                
            records.append({
                "timestamp": cur["timestamp"],
                "location": cur["location"],
                "current_speed": cur["current_speed"],
                "free_flow_speed": cur["free_flow_speed"],
                "congestion_percentage": cur["congestion_percentage"],
                "temperature": cur["temperature"],
                "rainfall": cur["rainfall"],
                "humidity": cur["humidity"],
                "prev_rainfall": cur["prev_rainfall"],
                "water_level": cur["water_level"],
                "aqi": cur["aqi"],
                "hour": cur["hour"],
                "day_of_week": cur["day_of_week"],
                # 30-minute forward condition prediction targets:
                "traffic_level": traffic_target,
                "flood_risk": flood_target
            })
            
    df = pd.DataFrame(records[:num_records])
    
    if output_path is None:
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        output_path = data_dir / "dataset.csv"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"Training dataset generated successfully: {len(df)} rows saved to {output_path}")
    return df

def generate_synthetic_dataset(num_records=12000, output_path=None):
    """Compatibility wrapper for generate_training_dataset."""
    return generate_training_dataset(num_records=num_records, output_path=output_path)

if __name__ == "__main__":
    generate_training_dataset()
