import sqlite3
import os
from pathlib import Path
from app import config

DB_DIR = Path(__file__).resolve().parent.parent.parent / "database"
DB_PATH = DB_DIR / "city.db"

INITIAL_LOCATIONS = [
    {
        "id": "central-junction",
        "name": "Central Junction",
        "lat": 11.0183,
        "lng": 76.9644,
        "zone_type": "Commercial Hub",
        "type": "traffic",
        "description": "Gandhipuram cross-cut transit intersection with high commuter influx."
    },
    {
        "id": "railway-station",
        "name": "Railway Station",
        "lat": 10.9984,
        "lng": 76.9632,
        "zone_type": "Transit Hub",
        "type": "transit",
        "description": "Coimbatore Main Junction Railway Station with continuous intercity traffic."
    },
    {
        "id": "airport-road",
        "name": "Airport Road",
        "lat": 11.0298,
        "lng": 77.0270,
        "zone_type": "Arterial Corridor",
        "type": "corridor",
        "description": "Avinashi Road arterial corridor connecting downtown to Airport and IT corridor."
    },
    {
        "id": "industrial-area",
        "name": "Industrial Area",
        "lat": 10.9425,
        "lng": 76.9790,
        "zone_type": "Industrial Cluster",
        "type": "industrial",
        "description": "SIDCO Kurichi industrial estate with manufacturing and freight movements."
    },
    {
        "id": "city-hospital",
        "name": "City Hospital",
        "lat": 10.9995,
        "lng": 76.9702,
        "zone_type": "Healthcare Corridor",
        "type": "healthcare",
        "description": "Coimbatore Medical College Hospital emergency corridor requiring rapid transit clearance."
    },
    {
        "id": "residential-zone",
        "name": "Residential Zone",
        "lat": 11.0102,
        "lng": 76.9492,
        "zone_type": "Residential Zone",
        "type": "residential",
        "description": "RS Puram residential and commercial area with schools and community centers."
    },
    {
        "id": "river-zone",
        "name": "River Zone",
        "lat": 10.9950,
        "lng": 77.0200,
        "zone_type": "Flood Prone Waterway",
        "type": "flood_prone",
        "description": "Low-lying Noyyal River and Singanallur lake overflow basin susceptible to runoff."
    },
    {
        "id": "bus-terminal",
        "name": "Bus Terminal",
        "lat": 11.0195,
        "lng": 76.9680,
        "zone_type": "Intercity Bus Terminal",
        "type": "transit",
        "description": "Gandhipuram Central & Omni Bus Terminals with frequent bus maneuvers."
    }
]

def get_db_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_column(cursor, table_name: str, column_name: str, column_def: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [row[1] for row in cursor.fetchall()]
    if column_name not in cols:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")

def init_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Master locations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        zone_type TEXT NOT NULL,
        description TEXT
    );
    """)
    _ensure_column(cursor, "locations", "type", "TEXT DEFAULT 'traffic'")

    # 2. OpenWeather observations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT DEFAULT 'openweather',
        city TEXT NOT NULL,
        temperature REAL NOT NULL,
        feels_like REAL,
        humidity REAL NOT NULL,
        pressure REAL,
        rainfall REAL NOT NULL,
        weather_condition TEXT NOT NULL,
        weather_details TEXT,
        wind_speed REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. OpenAQ observations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS air_quality_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT DEFAULT 'openaq',
        station_id INTEGER,
        location_name TEXT NOT NULL,
        pm25 REAL,
        pm10 REAL,
        no2 REAL,
        o3 REAL,
        co REAL,
        so2 REAL,
        aqi INTEGER NOT NULL,
        aqi_category TEXT NOT NULL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. TomTom Traffic observations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traffic_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id TEXT NOT NULL,
        source TEXT DEFAULT 'tomtom',
        current_speed REAL NOT NULL,
        free_flow_speed REAL NOT NULL,
        delay_seconds INTEGER NOT NULL,
        congestion_percentage REAL NOT NULL,
        traffic_condition TEXT NOT NULL,
        road_closure INTEGER DEFAULT 0,
        tomtom_confidence REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)

    # 5. Unified sensor observation snapshot per location
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id TEXT NOT NULL,
        vehicle_count INTEGER DEFAULT 0,
        traffic_speed REAL NOT NULL,
        traffic_level TEXT NOT NULL,
        aqi INTEGER NOT NULL,
        temperature REAL NOT NULL,
        rainfall REAL NOT NULL,
        water_level REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)
    _ensure_column(cursor, "sensor_data", "current_speed", "REAL DEFAULT 30.0")
    _ensure_column(cursor, "sensor_data", "free_flow_speed", "REAL DEFAULT 45.0")
    _ensure_column(cursor, "sensor_data", "congestion_percentage", "REAL DEFAULT 20.0")
    _ensure_column(cursor, "sensor_data", "traffic_source", "TEXT DEFAULT 'tomtom'")
    _ensure_column(cursor, "sensor_data", "aqi_category", "TEXT DEFAULT 'Moderate'")
    _ensure_column(cursor, "sensor_data", "aqi_source", "TEXT DEFAULT 'openaq'")
    _ensure_column(cursor, "sensor_data", "humidity", "REAL DEFAULT 60.0")
    _ensure_column(cursor, "sensor_data", "weather_condition", "TEXT DEFAULT 'Clear'")
    _ensure_column(cursor, "sensor_data", "weather_source", "TEXT DEFAULT 'openweather'")
    _ensure_column(cursor, "sensor_data", "water_level_source", "TEXT DEFAULT 'simulation'")
    _ensure_column(cursor, "sensor_data", "is_demo", "INTEGER DEFAULT 0")
    _ensure_column(cursor, "sensor_data", "demo_scenario", "TEXT")

    # 6. ML Predictions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id TEXT NOT NULL,
        traffic_pred TEXT NOT NULL,
        traffic_confidence REAL NOT NULL,
        flood_pred TEXT NOT NULL,
        flood_confidence REAL NOT NULL,
        horizon_min INTEGER DEFAULT 30,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)
    _ensure_column(cursor, "predictions", "traffic_probability", "REAL DEFAULT 85.0")
    _ensure_column(cursor, "predictions", "flood_probability", "REAL DEFAULT 85.0")
    _ensure_column(cursor, "predictions", "is_demo", "INTEGER DEFAULT 0")

    # 7. Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        message TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)
    _ensure_column(cursor, "alerts", "source", "TEXT DEFAULT 'sensor_evaluation'")

    # Re-sync / seed locations with Coimbatore coordinates
    for loc in INITIAL_LOCATIONS:
        cursor.execute(
            """
            INSERT INTO locations (id, name, lat, lng, zone_type, type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                lat=excluded.lat,
                lng=excluded.lng,
                zone_type=excluded.zone_type,
                type=excluded.type,
                description=excluded.description;
            """,
            (loc["id"], loc["name"], loc["lat"], loc["lng"], loc["zone_type"], loc["type"], loc["description"])
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
