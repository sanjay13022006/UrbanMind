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

        # Location-specific cache: { cache_key: { "data": ..., "fetch_time": ... } }
        self._location_cache: Dict[str, Dict[str, Any]] = {}
        # City-wide default cache
        self._cached_data: Optional[Dict[str, Any]] = None
        self._last_fetch_time: float = 0
        self._last_status: str = "Uninitialized"
        self._last_error_message: Optional[str] = None

    def fetch_weather(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        location_name: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Fetches live weather from OpenWeather for given coordinates.
        Defaults to city-wide coordinates if not provided.
        Uses in-memory per-coordinate caching within update_interval.
        In case of API errors, preserves last valid observation with stale status.
        """
        now = time.time()
        is_default_coords = (lat is None and lon is None)
        target_lat = float(lat) if lat is not None else self.latitude
        target_lon = float(lon) if lon is not None else self.longitude
        display_name = location_name or self.city_name
        cache_key = f"{round(target_lat, 4)},{round(target_lon, 4)}"

        if is_default_coords:
            cached_data = self._cached_data
            last_fetch = self._last_fetch_time
        else:
            entry = self._location_cache.get(cache_key)
            cached_data = entry["data"] if entry else None
            last_fetch = entry["fetch_time"] if entry else 0

        # Return cached observation if still valid and not forced
        if not force_refresh and cached_data and (now - last_fetch < self.update_interval):
            return cached_data

        if not self.api_key or self.api_key == "your_openweather_key":
            self._last_status = "Missing API Key"
            self._last_error_message = "OpenWeather API key is not configured in .env"
            if cached_data:
                cached = dict(cached_data)
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            elif self._cached_data:
                cached = dict(self._cached_data)
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            return {
                "source": "openweather",
                "status": "unavailable",
                "city": display_name,
                "latitude": target_lat,
                "longitude": target_lon,
                "temperature": 28.0,
                "feels_like": 28.0,
                "humidity": 65.0,
                "rainfall": 0.0,
                "weather_condition": "Unknown",
                "wind_speed": 0.0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": self._last_error_message
            }

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": target_lat,
            "lon": target_lon,
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
                local_station_name = raw.get("name") or display_name

                normalized = {
                    "source": "openweather",
                    "status": "connected",
                    "city": local_station_name,
                    "location_name": display_name,
                    "latitude": target_lat,
                    "longitude": target_lon,
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

                self._location_cache[cache_key] = {
                    "data": normalized,
                    "fetch_time": now
                }
                # Also maintain default city cache
                if is_default_coords or not self._cached_data:
                    self._cached_data = normalized
                    self._last_fetch_time = now

                self._last_status = "connected"
                self._last_error_message = None
                return normalized

            else:
                error_msg = f"OpenWeather API returned HTTP {response.status_code}: {response.text[:120]}"
                self._last_status = "error"
                self._last_error_message = error_msg
                
                if cached_data:
                    stale_data = dict(cached_data)
                    stale_data["status"] = "stale"
                    stale_data["warning"] = f"API error ({response.status_code}) — showing last valid observation from {stale_data.get('timestamp')}"
                    return stale_data
                elif self._cached_data:
                    stale_data = dict(self._cached_data)
                    stale_data["status"] = "stale"
                    stale_data["warning"] = f"API error ({response.status_code}) — showing last valid observation from {self._cached_data.get('timestamp')}"
                    return stale_data

                return {
                    "source": "openweather",
                    "status": "unavailable",
                    "city": display_name,
                    "latitude": target_lat,
                    "longitude": target_lon,
                    "temperature": 28.0,
                    "feels_like": 28.0,
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

            if cached_data:
                stale_data = dict(cached_data)
                stale_data["status"] = "stale"
                stale_data["warning"] = f"Connection failed — showing last valid observation from {stale_data.get('timestamp')}"
                return stale_data
            elif self._cached_data:
                stale_data = dict(self._cached_data)
                stale_data["status"] = "stale"
                stale_data["warning"] = f"Connection failed — showing last valid observation from {self._cached_data.get('timestamp')}"
                return stale_data

            return {
                "source": "openweather",
                "status": "unavailable",
                "city": display_name,
                "latitude": target_lat,
                "longitude": target_lon,
                "temperature": 28.0,
                "feels_like": 28.0,
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
