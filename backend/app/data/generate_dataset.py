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

def generate_synthetic_dataset(num_records=8000, output_path=None):
    np.random.seed(42)
    start_date = datetime.datetime(2026, 8, 1, 0, 0, 0)
    
    records = []
    
    for i in range(num_records):
        # Time steps every 15 minutes across locations
        time_offset_min = (i // len(LOCATIONS)) * 15
        dt = start_date + datetime.timedelta(minutes=time_offset_min)
        loc = LOCATIONS[i % len(LOCATIONS)]
        
        hour = dt.hour
        day_of_week = dt.weekday() # 0 = Monday, 6 = Sunday
        
        # Rush hour check (8-10 AM, 5-8 PM on weekdays)
        is_weekday = day_of_week < 5
        is_rush = is_weekday and ((8 <= hour <= 10) or (17 <= hour <= 20))
        
        # Location specific baseline modifiers
        loc_traffic_bias = 1.3 if loc in ["central-junction", "railway-station", "bus-terminal"] else 1.0
        loc_aqi_bias = 1.4 if loc == "industrial-area" else 1.0
        loc_water_bias = 1.5 if loc == "river-zone" else 0.8
        
        # Weather simulation
        # Random rain event probability
        is_rainy_day = np.random.rand() < 0.25
        rainfall = np.random.uniform(20, 90) if is_rainy_day and np.random.rand() < 0.6 else np.random.uniform(0, 10)
        if np.random.rand() < 0.05: # Flash heavy storm
            rainfall = np.random.uniform(70, 140)
            
        temperature = np.random.uniform(22, 36) - (rainfall * 0.08)
        temperature = round(temperature, 1)
        rainfall = round(rainfall, 1)
        
        # Water level correlates with rainfall & river location
        base_water = 0.5 * loc_water_bias
        water_level = base_water + (rainfall * 0.035) + np.random.uniform(-0.1, 0.2)
        water_level = max(0.2, round(water_level, 2))
        
        # Vehicle count and speed calculation
        base_vehicles = np.random.uniform(20, 50)
        if is_rush:
            base_vehicles *= np.random.uniform(2.2, 3.5)
        else:
            base_vehicles *= np.random.uniform(0.8, 1.4)
            
        vehicle_count = int(base_vehicles * loc_traffic_bias)
        vehicle_count = max(5, vehicle_count)
        
        # Speed drops as vehicle count increases and rain increases
        speed = 65 - (vehicle_count * 0.22) - (rainfall * 0.15) + np.random.uniform(-3, 3)
        traffic_speed = max(5.0, round(speed, 1))
        
        # AQI calculation
        base_aqi = np.random.uniform(35, 75) * loc_aqi_bias
        aqi_add = (vehicle_count * 0.25) - (rainfall * 0.1)
        aqi = int(max(15, base_aqi + aqi_add + np.random.uniform(-5, 10)))
        
        # Derive Traffic Congestion Level Target (Low, Moderate, High, Critical)
        # Congestion score calculation
        congestion_index = (vehicle_count / (traffic_speed + 1.0)) * (1.1 if rainfall > 30 else 1.0)
        
        if congestion_index < 1.2:
            traffic_level = "Low"
        elif congestion_index < 3.2:
            traffic_level = "Moderate"
        elif congestion_index < 6.0:
            traffic_level = "High"
        else:
            traffic_level = "Critical"
            
        # Derive Flood Risk Target (Low, Moderate, High, Critical)
        # Prev rainfall simulation
        prev_rainfall = max(0.0, rainfall * np.random.uniform(0.4, 0.9))
        prev_rainfall = round(prev_rainfall, 1)
        
        flood_index = (rainfall * 0.45) + (water_level * 18.0) + (prev_rainfall * 0.25)
        if flood_index < 25:
            flood_risk = "Low"
        elif flood_index < 50:
            flood_risk = "Moderate"
        elif flood_index < 75:
            flood_risk = "High"
        else:
            flood_risk = "Critical"
            
        records.append({
            "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "location": loc,
            "vehicle_count": vehicle_count,
            "traffic_speed": traffic_speed,
            "aqi": aqi,
            "temperature": temperature,
            "rainfall": rainfall,
            "prev_rainfall": prev_rainfall,
            "water_level": water_level,
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
    print(f"Dataset generated successfully with {len(df)} records at {output_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_dataset()
