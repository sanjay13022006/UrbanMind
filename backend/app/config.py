import os
from pathlib import Path
from dotenv import load_dotenv

# Locate .env file relative to backend root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "").strip()
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "").strip()

CITY_NAME = os.getenv("CITY_NAME", "Coimbatore").strip()
try:
    LATITUDE = float(os.getenv("LATITUDE", "11.0168"))
    LONGITUDE = float(os.getenv("LONGITUDE", "76.9558"))
except ValueError:
    LATITUDE = 11.0168
    LONGITUDE = 76.9558

WEATHER_UPDATE_INTERVAL = int(os.getenv("WEATHER_UPDATE_INTERVAL", "300"))
AIR_QUALITY_UPDATE_INTERVAL = int(os.getenv("AIR_QUALITY_UPDATE_INTERVAL", "300"))
TRAFFIC_UPDATE_INTERVAL = int(os.getenv("TRAFFIC_UPDATE_INTERVAL", "120"))
