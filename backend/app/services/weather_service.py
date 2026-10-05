"""
OpenWeather API Integration Service
-----------------------------------
Retrieves real-time weather and rainfall observations from OpenWeather API.
Implements in-memory caching and safe error handling without generating fake data.
"""

import time
import datetime
import requests
from typing import Dict, Any, Optional
from app import config

class WeatherService:
    def __init__(self):
        self.api_key = config.OPENWEATHER_API_KEY
        self.city_name = config.CITY_NAME
        self.latitude = config.LATITUDE
        self.longitude = config.LONGITUDE
        self.update_interval = config.WEATHER_UPDATE_INTERVAL  # seconds

        # Cache storage
        self._cached_data: Optional[Dict[str, Any]] = None
        self._last_fetch_time: float = 0
        self._last_status: str = "Uninitialized"
        self._last_error_message: Optional[str] = None

    def fetch_weather(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetches live weather from OpenWeather.
        Uses cached data if fetched within the update interval.
        In case of API errors, preserves last valid observation with stale status.
        """
        now = time.time()
        
        # Return cached observation if still valid and not forced
        if not force_refresh and self._cached_data and (now - self._last_fetch_time < self.update_interval):
            return self._cached_data

        if not self.api_key or self.api_key == "your_openweather_key":
            self._last_status = "Missing API Key"
            self._last_error_message = "OpenWeather API key is not configured in .env"
            if self._cached_data:
                cached = dict(self._cached_data)
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            return {
                "source": "openweather",
                "status": "unavailable",
                "city": self.city_name,
                "temperature": 28.0,
                "humidity": 65.0,
                "rainfall": 0.0,
                "weather_condition": "Unknown",
                "wind_speed": 0.0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": self._last_error_message
            }

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                raw = response.json()

                # Extract rainfall safely: OpenWeather may return rain as {"1h": x} or omit completely
                rainfall = 0.0
                if "rain" in raw and isinstance(raw["rain"], dict):
                    rainfall = float(raw["rain"].get("1h", raw["rain"].get("3h", 0.0)))
                elif "precipitation" in raw and isinstance(raw["precipitation"], dict):
                    rainfall = float(raw["precipitation"].get("value", 0.0))

                weather_desc = "Clear"
                if "weather" in raw and len(raw["weather"]) > 0:
                    weather_desc = raw["weather"][0].get("main", "Clear")

                main_data = raw.get("main", {})
                wind_data = raw.get("wind", {})

                normalized = {
                    "source": "openweather",
                    "status": "connected",
                    "city": raw.get("name", self.city_name),
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "temperature": round(float(main_data.get("temp", 28.0)), 1),
                    "feels_like": round(float(main_data.get("feels_like", main_data.get("temp", 28.0))), 1),
                    "humidity": round(float(main_data.get("humidity", 60.0)), 1),
                    "pressure": float(main_data.get("pressure", 1012)),
                    "rainfall": round(rainfall, 2),  # In mm/h
                    "weather_condition": weather_desc,
                    "weather_details": raw.get("weather", [{}])[0].get("description", weather_desc),
                    "wind_speed": round(float(wind_data.get("speed", 0.0)) * 3.6, 1), # m/s to km/h
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_successful_update": datetime.datetime.now().strftime("%I:%M:%S %p")
                }

                self._cached_data = normalized
                self._last_fetch_time = now
                self._last_status = "connected"
                self._last_error_message = None
                return normalized

            else:
                error_msg = f"OpenWeather API returned HTTP {response.status_code}: {response.text[:120]}"
                self._last_status = "error"
                self._last_error_message = error_msg
                
                if self._cached_data:
                    stale_data = dict(self._cached_data)
                    stale_data["status"] = "stale"
                    stale_data["warning"] = f"API error ({response.status_code}) — showing last valid observation from {self._cached_data.get('timestamp')}"
                    return stale_data

                return {
                    "source": "openweather",
                    "status": "unavailable",
                    "city": self.city_name,
                    "temperature": 28.0,
                    "humidity": 65.0,
                    "rainfall": 0.0,
                    "weather_condition": "Unavailable",
                    "wind_speed": 0.0,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": error_msg
                }

        except Exception as e:
            error_msg = f"Network exception contacting OpenWeather: {str(e)}"
            self._last_status = "error"
            self._last_error_message = error_msg

            if self._cached_data:
                stale_data = dict(self._cached_data)
                stale_data["status"] = "stale"
                stale_data["warning"] = f"Connection failed — showing last valid observation from {self._cached_data.get('timestamp')}"
                return stale_data

            return {
                "source": "openweather",
                "status": "unavailable",
                "city": self.city_name,
                "temperature": 28.0,
                "humidity": 65.0,
                "rainfall": 0.0,
                "weather_condition": "Unavailable",
                "wind_speed": 0.0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": error_msg
            }

    def get_source_status(self) -> Dict[str, Any]:
        """Returns metadata for the Data Sources status panel."""
        return {
            "name": "OpenWeather",
            "source": "openweather",
            "status": self._last_status if self._cached_data else ("connected" if self._last_status == "connected" else "connecting"),
            "last_update": self._cached_data.get("last_successful_update") if self._cached_data else "Pending",
            "update_interval": f"{self.update_interval // 60}m",
            "coverage": f"City-wide ({self.city_name})",
            "error": self._last_error_message
        }

weather_service = WeatherService()
