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
        "zone_type": "Residential & Retail",
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
    },
    {
        "id": "ukkadam-junction",
        "name": "Ukkadam Bus Stand & Lake",
        "lat": 10.9906,
        "lng": 76.9630,
        "zone_type": "Transit & Waterway",
        "type": "transit",
        "description": "South transit hub adjacent to Periyakulam lake basin and Pollachi road."
    },
    {
        "id": "tidel-park",
        "name": "TIDEL Park IT Corridor",
        "lat": 11.0245,
        "lng": 77.0225,
        "zone_type": "Technology SEZ",
        "type": "tech",
        "description": "Major IT technology park and educational hub with high peak-hour tech commuter density."
    },
    {
        "id": "saravanampatti",
        "name": "Saravanampatti Tech Hub",
        "lat": 11.0748,
        "lng": 77.0022,
        "zone_type": "IT & Arterial Highway",
        "type": "tech",
        "description": "CHIL SEZ IT corridor on Sathy Road with prominent tech parks and colleges."
    },
    {
        "id": "town-hall",
        "name": "Town Hall & Big Bazaar",
        "lat": 10.9954,
        "lng": 76.9570,
        "zone_type": "Historic Commercial Core",
        "type": "commercial",
        "description": "Dense traditional marketplace and commercial district with tight lanes."
    },
    {
        "id": "saibaba-colony",
        "name": "Saibaba Colony",
        "lat": 11.0226,
        "lng": 76.9408,
        "zone_type": "Commercial & Residential",
        "type": "commercial",
        "description": "NSR Road retail corridor and Mettupalayam road intersection."
    },
    {
        "id": "ganapathy-junction",
        "name": "Ganapathy Junction",
        "lat": 11.0319,
        "lng": 76.9811,
        "zone_type": "Textile & Residential",
        "type": "traffic",
        "description": "Sathy Road junction linking industrial textile units with dense urban residences."
    },
    {
        "id": "ramanathapuram",
        "name": "Ramanathapuram Junction",
        "lat": 10.9899,
        "lng": 76.9855,
        "zone_type": "Arterial Chokepoint",
        "type": "traffic",
        "description": "Trichy Road key intersection connecting city center to Singanallur."
    },
    {
        "id": "singanallur-junction",
        "name": "Singanallur Bus Terminal",
        "lat": 11.0040,
        "lng": 77.0242,
        "zone_type": "East Transit Hub",
        "type": "transit",
        "description": "East mofussil bus terminal and Trichy Road industrial corridor nexus."
    },
    {
        "id": "hopes-college",
        "name": "Hopes College Junction",
        "lat": 11.0230,
        "lng": 77.0090,
        "zone_type": "Educational & Transit",
        "type": "traffic",
        "description": "Avinashi Road high-density educational institution chokepoint."
    },
    {
        "id": "valankulam-lake",
        "name": "Valankulam Lake Promenade",
        "lat": 11.0010,
        "lng": 76.9760,
        "zone_type": "Waterfront Basin & Wetland",
        "type": "flood_prone",
        "description": "Smart City lakefront promenade and wetland basin sensitive to urban runoff."
    },
    {
        "id": "perur-corridor",
        "name": "Perur Heritage Corridor",
        "lat": 10.9736,
        "lng": 76.9282,
        "zone_type": "Cultural & Riparian",
        "type": "flood_prone",
        "description": "Historic temple corridor along Noyyal river basin and Siruvani road."
    },
    {
        "id": "vadavalli",
        "name": "Vadavalli Junction",
        "lat": 11.0250,
        "lng": 76.9038,
        "zone_type": "West Residential Arterial",
        "type": "residential",
        "description": "Maruthamalai arterial road connecting universities and residential layouts."
    },
    {
        "id": "thudiyalur",
        "name": "Thudiyalur Junction",
        "lat": 11.0680,
        "lng": 76.9356,
        "zone_type": "North Highway Bottleneck",
        "type": "traffic",
        "description": "Mettupalayam Highway bottleneck connecting north suburbs to Nilgiris freight route."
    },
    {
        "id": "eachanari",
        "name": "Eachanari Industrial Highway",
        "lat": 10.9270,
        "lng": 76.9740,
        "zone_type": "Freight & Industrial",
        "type": "industrial",
        "description": "Pollachi highway industrial sector with heavy transport vehicle volume."
    },
    {
        "id": "race-course",
        "name": "Race Course Promenade",
        "lat": 11.0060,
        "lng": 76.9730,
        "zone_type": "Administrative & Green",
        "type": "commercial",
        "description": "Administrative hub with collectorate, judicial complex, and walking promenade."
    },
    {
        "id": "kovai-pudur",
        "name": "Kovai Pudur Foothills",
        "lat": 10.9380,
        "lng": 76.9360,
        "zone_type": "Suburban Foothill",
        "type": "residential",
        "description": "Southwest residential township located at the Western Ghats foothill zone."
    }
]

def get_db_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
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
        delay_seconds INTEGER,
        current_travel_time INTEGER,
        free_flow_travel_time INTEGER,
        congestion_percentage REAL NOT NULL,
        traffic_condition TEXT NOT NULL,
        road_closure INTEGER DEFAULT 0,
        tomtom_confidence REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)

    # Migrate traffic_data if delay_seconds has legacy NOT NULL constraint
    cursor.execute("PRAGMA table_info(traffic_data)")
    t_cols = {row["name"]: dict(row) for row in cursor.fetchall()}
    if t_cols.get("delay_seconds", {}).get("notnull") == 1:
        cursor.execute("DROP TABLE IF EXISTS traffic_data_migrated;")
        cursor.execute("""
            CREATE TABLE traffic_data_migrated (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id TEXT NOT NULL,
                source TEXT DEFAULT 'tomtom',
                current_speed REAL NOT NULL,
                free_flow_speed REAL NOT NULL,
                delay_seconds INTEGER,
                current_travel_time INTEGER,
                free_flow_travel_time INTEGER,
                congestion_percentage REAL NOT NULL,
                traffic_condition TEXT NOT NULL,
                road_closure INTEGER DEFAULT 0,
                tomtom_confidence REAL,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (location_id) REFERENCES locations(id)
            );
        """)
        has_cur_tt = "current_travel_time" in t_cols
        has_ff_tt = "free_flow_travel_time" in t_cols
        cur_tt_expr = "current_travel_time" if has_cur_tt else "NULL"
        ff_tt_expr = "free_flow_travel_time" if has_ff_tt else "NULL"
        cursor.execute(f"""
            INSERT INTO traffic_data_migrated (
                id, location_id, source, current_speed, free_flow_speed,
                delay_seconds, current_travel_time, free_flow_travel_time,
                congestion_percentage, traffic_condition, road_closure,
                tomtom_confidence, status, timestamp
            )
            SELECT 
                id, location_id, source, current_speed, free_flow_speed,
                delay_seconds, 
                {cur_tt_expr},
                {ff_tt_expr},
                congestion_percentage, traffic_condition, road_closure,
                tomtom_confidence, status, timestamp
            FROM traffic_data;
        """)
        cursor.execute("DROP TABLE traffic_data;")
        cursor.execute("ALTER TABLE traffic_data_migrated RENAME TO traffic_data;")

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
    _ensure_column(cursor, "traffic_data", "current_travel_time", "INTEGER")
    _ensure_column(cursor, "traffic_data", "free_flow_travel_time", "INTEGER")

    _ensure_column(cursor, "sensor_data", "current_speed", "REAL DEFAULT 30.0")
    _ensure_column(cursor, "sensor_data", "free_flow_speed", "REAL DEFAULT 45.0")
    _ensure_column(cursor, "sensor_data", "congestion_percentage", "REAL DEFAULT 20.0")
    _ensure_column(cursor, "sensor_data", "delay_seconds", "INTEGER")
    _ensure_column(cursor, "sensor_data", "current_travel_time", "INTEGER")
    _ensure_column(cursor, "sensor_data", "free_flow_travel_time", "INTEGER")
    _ensure_column(cursor, "sensor_data", "traffic_source", "TEXT DEFAULT 'tomtom'")
    _ensure_column(cursor, "sensor_data", "traffic_status", "TEXT DEFAULT 'connected'")
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
