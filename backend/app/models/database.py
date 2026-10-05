import sqlite3
import os
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent.parent / "database"
DB_PATH = DB_DIR / "city.db"

INITIAL_LOCATIONS = [
    {
        "id": "central-junction",
        "name": "Central Junction",
        "lat": 12.9716,
        "lng": 77.5946,
        "zone_type": "Commercial",
        "description": "Primary downtown transit intersection with high congestion vulnerability."
    },
    {
        "id": "railway-station",
        "name": "Railway Station",
        "lat": 12.9782,
        "lng": 77.5695,
        "zone_type": "Transit Hub",
        "description": "Major intercity passenger terminal with constant commuter influx."
    },
    {
        "id": "airport-road",
        "name": "Airport Road",
        "lat": 12.9900,
        "lng": 77.6400,
        "zone_type": "Arterial Corridor",
        "description": "High-speed multi-lane arterial connecting downtown to northern gateway."
    },
    {
        "id": "industrial-area",
        "name": "Industrial Area",
        "lat": 12.9400,
        "lng": 77.5500,
        "zone_type": "Industrial",
        "description": "Manufacturing cluster with heavy vehicle traffic and air emissions."
    },
    {
        "id": "city-hospital",
        "name": "City Hospital",
        "lat": 12.9600,
        "lng": 77.5900,
        "zone_type": "Healthcare Zone",
        "description": "Critical emergency care zone requiring prioritized traffic clearance."
    },
    {
        "id": "residential-zone",
        "name": "Residential Zone",
        "lat": 12.9300,
        "lng": 77.6100,
        "zone_type": "Residential",
        "description": "High-density residential neighborhood with school and market zones."
    },
    {
        "id": "river-zone",
        "name": "River Zone",
        "lat": 12.9550,
        "lng": 77.6350,
        "zone_type": "Waterfront / Flood Prone",
        "description": "Low-lying river basin vulnerable to rapid runoff and flooding during heavy rainfall."
    },
    {
        "id": "bus-terminal",
        "name": "Bus Terminal",
        "lat": 12.9750,
        "lng": 77.5750,
        "zone_type": "Transit Hub",
        "description": "Central intra-city bus deport with heavy pedestrian and bus maneuvers."
    }
]

def get_db_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id TEXT NOT NULL,
        vehicle_count INTEGER NOT NULL,
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

    # Seed locations if empty
    cursor.execute("SELECT COUNT(*) as count FROM locations;")
    if cursor.fetchone()["count"] == 0:
        for loc in INITIAL_LOCATIONS:
            cursor.execute(
                "INSERT INTO locations (id, name, lat, lng, zone_type, description) VALUES (?, ?, ?, ?, ?, ?)",
                (loc["id"], loc["name"], loc["lat"], loc["lng"], loc["zone_type"], loc["description"])
            )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
