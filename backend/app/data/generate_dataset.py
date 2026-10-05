import pandas as pd
import numpy as np
import datetime
from pathlib import Path

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

def generate_training_dataset(num_records=10000, output_path=None):
    """
    Generates a realistic historical dataset for offline ML model training.
    Features align strictly with real-world API telemetry inputs:
    - TomTom: current_speed, free_flow_speed, congestion_percentage
    - OpenWeather: temperature, rainfall, humidity
    - OpenAQ: aqi
    - Controlled Hydrology: water_level, prev_rainfall
    NO fake vehicle count is used in production feature engineering.
    """
    np.random.seed(42)
    start_date = datetime.datetime(2026, 7, 1, 0, 0, 0)
    
    records = []
    
    for i in range(num_records):
        time_offset_min = (i // len(LOCATIONS)) * 15
        dt = start_date + datetime.timedelta(minutes=time_offset_min)
        loc = LOCATIONS[i % len(LOCATIONS)]
        
        hour = dt.hour
        day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
        is_weekday = day_of_week < 5
        is_rush = is_weekday and ((8 <= hour <= 10) or (17 <= hour <= 20))
        
        # Environmental Weather Simulation (OpenWeather features)
        is_rainy = np.random.rand() < 0.22
        if is_rainy:
            rainfall = np.random.uniform(5.0, 75.0)
            if np.random.rand() < 0.08:
                rainfall = np.random.uniform(75.0, 130.0)  # Cloudburst
        else:
            rainfall = 0.0 if np.random.rand() < 0.85 else np.random.uniform(0.1, 3.0)
            
        temperature = round(float(np.random.uniform(22.0, 36.0) - (rainfall * 0.08)), 1)
        humidity = round(float(np.clip(50.0 + (rainfall * 0.4) + np.random.uniform(-10, 15), 30.0, 98.0)), 1)
        prev_rainfall = round(float(max(0.0, rainfall * np.random.uniform(0.3, 0.85))), 1)

        # Hydrological Water Level (Simulated basin response to rainfall)
        loc_water_bias = 1.4 if loc == "river-zone" else 0.75
        base_water = 0.6 * loc_water_bias
        water_level = base_water + (rainfall * 0.03) + (prev_rainfall * 0.015) + np.random.uniform(-0.05, 0.08)
        water_level = round(float(max(0.3, water_level)), 2)

        # Air Quality (OpenAQ feature)
        loc_aqi_bias = 1.35 if loc == "industrial-area" else 1.0
        base_aqi = np.random.uniform(40, 80) * loc_aqi_bias
        # Traffic slows down and weather affects AQI (rain washes pollutants down)
        rain_wash = rainfall * 0.35
        aqi = int(np.clip(base_aqi - rain_wash + np.random.uniform(-8, 12), 20, 240))

        # Traffic Flow Simulation (TomTom features: free_flow_speed, current_speed, congestion_percentage)
        free_flow_speed = 50.0 if loc in ["airport-road"] else 40.0
        if loc in ["central-junction", "bus-terminal", "railway-station"]:
            free_flow_speed = 35.0

        if is_rush:
            congestion_factor = np.random.uniform(0.45, 0.85)
        else:
            congestion_factor = np.random.uniform(0.05, 0.40)

        # Rain impacts traffic speeds
        if rainfall > 20.0:
            congestion_factor = min(0.95, congestion_factor + 0.20)

        current_speed = round(float(free_flow_speed * (1.0 - congestion_factor) + np.random.uniform(-2, 2)), 1)
        current_speed = max(4.0, min(free_flow_speed, current_speed))
        
        congestion_pct = round(max(0.0, (free_flow_speed - current_speed) / free_flow_speed * 100.0), 1)

        # Traffic Level Ground Truth
        if congestion_pct >= 60.0 or current_speed < 12.0:
            traffic_level = "Critical"
        elif congestion_pct >= 40.0 or current_speed < 22.0:
            traffic_level = "High"
        elif congestion_pct >= 20.0 or current_speed < 32.0:
            traffic_level = "Moderate"
        else:
            traffic_level = "Low"

        # Flood Risk Ground Truth
        flood_index = (rainfall * 0.45) + (prev_rainfall * 0.25) + (water_level * 18.0)
        if flood_index >= 75 or water_level > 2.8 or rainfall > 85.0:
            flood_risk = "Critical"
        elif flood_index >= 50 or water_level > 2.0 or rainfall > 45.0:
            flood_risk = "High"
        elif flood_index >= 25 or water_level > 1.2 or rainfall > 15.0:
            flood_risk = "Moderate"
        else:
            flood_risk = "Low"

        records.append({
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
            "traffic_level": traffic_level,
            "flood_risk": flood_risk
        })

    df = pd.DataFrame(records)
    
    if output_path is None:
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        output_path = data_dir / "dataset.csv"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"Training dataset generated successfully: {len(df)} rows at {output_path}")
    return df

if __name__ == "__main__":
    generate_training_dataset()
