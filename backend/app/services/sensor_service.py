import random
import datetime
from app.models.database import get_db_connection, INITIAL_LOCATIONS

# Scenario definitions
SCENARIOS = {
    "normal": "Normal City Traffic & Weather",
    "rush_hour": "Rush Hour Congestion",
    "heavy_rain": "Heavy Rain & Flood Warning"
}

class SensorService:
    def __init__(self):
        self.current_scenario = "normal"

    def set_scenario(self, scenario_name: str):
        if scenario_name in SCENARIOS:
            self.current_scenario = scenario_name
            return True
        return False

    def generate_sensor_tick(self, scenario_override=None):
        scenario = scenario_override or self.current_scenario
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get latest reading for each location to generate smooth realistic step
        cursor.execute("SELECT * FROM locations")
        locations = cursor.fetchall()
        
        now = datetime.datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

        new_readings = []

        for loc in locations:
            loc_id = loc["id"]
            
            # Fetch previous sensor state if available
            cursor.execute(
                "SELECT * FROM sensor_data WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1",
                (loc_id,)
            )
            prev = cursor.fetchone()

            if prev and scenario == "normal":
                # Smooth drift around normal values
                p_v = prev["vehicle_count"]
                p_s = prev["traffic_speed"]
                p_aqi = prev["aqi"]
                p_temp = prev["temperature"]
                p_rain = prev["rainfall"]
                p_w = prev["water_level"]

                vehicle_count = max(15, min(110, int(p_v + random.randint(-4, 5))))
                speed_delta = -0.3 if vehicle_count > p_v else 0.3
                traffic_speed = max(25.0, min(65.0, round(p_s + speed_delta + random.uniform(-1.0, 1.0), 1)))
                aqi = max(25, min(95, int(p_aqi + random.randint(-2, 3))))
                temperature = max(24.0, min(34.0, round(p_temp + random.uniform(-0.2, 0.2), 1)))
                rainfall = max(0.0, min(12.0, round(p_rain + random.uniform(-0.5, 0.5), 1)))
                water_level = max(0.4, min(1.3, round(p_w + random.uniform(-0.02, 0.02), 2)))

            elif scenario == "rush_hour":
                # Rush hour: high vehicle count, low speed, higher AQI, especially at junctions/transit
                if loc_id in ["central-junction", "railway-station", "bus-terminal", "airport-road"]:
                    vehicle_count = random.randint(140, 220)
                    traffic_speed = round(random.uniform(8.0, 19.0), 1)
                    aqi = random.randint(110, 160)
                else:
                    vehicle_count = random.randint(85, 130)
                    traffic_speed = round(random.uniform(22.0, 35.0), 1)
                    aqi = random.randint(75, 105)

                temperature = round(random.uniform(28.0, 33.0), 1)
                rainfall = round(random.uniform(0.0, 8.0), 1)
                water_level = round(random.uniform(0.7, 1.3), 2)

            elif scenario == "heavy_rain":
                # Heavy rain: intense rainfall, high water level (especially River Zone), reduced speed
                if loc_id == "river-zone":
                    water_level = round(random.uniform(3.2, 4.8), 2)
                    rainfall = round(random.uniform(85.0, 135.0), 1)
                else:
                    water_level = round(random.uniform(1.8, 2.9), 2)
                    rainfall = round(random.uniform(65.0, 105.0), 1)

                vehicle_count = random.randint(75, 125)
                traffic_speed = round(random.uniform(12.0, 26.0), 1)
                aqi = random.randint(35, 65) # Rain washes pollutants
                temperature = round(random.uniform(21.0, 25.0), 1)

            else: # Default normal initial values
                vehicle_count = random.randint(40, 75)
                traffic_speed = round(random.uniform(40.0, 58.0), 1)
                aqi = random.randint(45, 80)
                temperature = round(random.uniform(26.0, 31.0), 1)
                rainfall = round(random.uniform(0.0, 5.0), 1)
                water_level = round(random.uniform(0.6, 1.1), 2)

            # Determine instant traffic label heuristically for raw table
            if vehicle_count > 150 or traffic_speed < 15:
                traffic_level = "Critical"
            elif vehicle_count > 100 or traffic_speed < 25:
                traffic_level = "High"
            elif vehicle_count > 60 or traffic_speed < 40:
                traffic_level = "Moderate"
            else:
                traffic_level = "Low"

            cursor.execute(
                """
                INSERT INTO sensor_data 
                (location_id, vehicle_count, traffic_speed, traffic_level, aqi, temperature, rainfall, water_level, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (loc_id, vehicle_count, traffic_speed, traffic_level, aqi, temperature, rainfall, water_level, timestamp_str)
            )

            new_readings.append({
                "location_id": loc_id,
                "vehicle_count": vehicle_count,
                "traffic_speed": traffic_speed,
                "traffic_level": traffic_level,
                "aqi": aqi,
                "temperature": temperature,
                "rainfall": rainfall,
                "water_level": water_level,
                "hour": hour,
                "day_of_week": day_of_week,
                "timestamp": timestamp_str
            })

        conn.commit()
        conn.close()
        return new_readings

sensor_service = SensorService()
