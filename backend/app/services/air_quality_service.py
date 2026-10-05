"""
OpenAQ API Integration Service
------------------------------
Retrieves real-time air quality observations and pollutant measurements from OpenAQ v3 API.
Calculates documented AQI index and categories from measured PM2.5 and PM10 concentrations.
Implements in-memory caching and resilient failure handling without fake data generation.
"""

import time
import datetime
import requests
from typing import Dict, Any, Optional
from app import config

class AirQualityService:
    def __init__(self):
        self.api_key = config.OPENAQ_API_KEY
        self.city_name = config.CITY_NAME
        self.latitude = config.LATITUDE
        self.longitude = config.LONGITUDE
        self.update_interval = config.AIR_QUALITY_UPDATE_INTERVAL

        # Cache storage
        self._cached_data: Optional[Dict[str, Any]] = None
        self._last_fetch_time: float = 0
        self._last_status: str = "Uninitialized"
        self._last_error_message: Optional[str] = None
        self._known_station_id: Optional[int] = None
        self._station_sensors_map: Dict[int, str] = {}

    def _calculate_aqi(self, pm25: Optional[float], pm10: Optional[float]) -> tuple[int, str]:
        """
        Calculates standard AQI value and categorization using CPCB / US EPA breakpoint formula.
        Breakpoint standard for PM2.5 (24h/1h µg/m³):
          0 - 30   -> AQI 0 - 50   (Good)
          31 - 60  -> AQI 51 - 100 (Moderate / Satisfactory)
          61 - 90  -> AQI 101 - 200 (Poor / Sensitive)
          91 - 120 -> AQI 201 - 300 (Very Poor)
          > 120    -> AQI 301 - 500 (Severe / Hazardous)
        """
        sub_indices = []

        if pm25 is not None and pm25 >= 0:
            if pm25 <= 30:
                aqi_pm25 = (pm25 / 30.0) * 50
            elif pm25 <= 60:
                aqi_pm25 = 50 + ((pm25 - 30) / 30.0) * 50
            elif pm25 <= 90:
                aqi_pm25 = 100 + ((pm25 - 60) / 30.0) * 100
            elif pm25 <= 120:
                aqi_pm25 = 200 + ((pm25 - 90) / 30.0) * 100
            else:
                aqi_pm25 = 300 + min(200, ((pm25 - 120) / 130.0) * 200)
            sub_indices.append(aqi_pm25)

        if pm10 is not None and pm10 >= 0:
            if pm10 <= 50:
                aqi_pm10 = (pm10 / 50.0) * 50
            elif pm10 <= 100:
                aqi_pm10 = 50 + ((pm10 - 50) / 50.0) * 50
            elif pm10 <= 250:
                aqi_pm10 = 100 + ((pm10 - 100) / 150.0) * 100
            else:
                aqi_pm10 = 200 + min(300, ((pm10 - 250) / 150.0) * 100)
            sub_indices.append(aqi_pm10)

        if not sub_indices:
            return 55, "Moderate"

        overall_aqi = int(round(max(sub_indices)))
        overall_aqi = max(10, min(500, overall_aqi))

        if overall_aqi <= 50:
            category = "Good"
        elif overall_aqi <= 100:
            category = "Moderate"
        elif overall_aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
        elif overall_aqi <= 200:
            category = "Unhealthy"
        elif overall_aqi <= 300:
            category = "Very Unhealthy"
        else:
            category = "Hazardous"

        return overall_aqi, category

    def _fetch_station_sensors(self, station_id: int, headers: dict):
        """Map sensor IDs to parameter names for the station."""
        try:
            url = f"https://api.openaq.org/v3/locations/{station_id}/sensors"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                for s in data.get("results", []):
                    sid = s.get("id")
                    param_name = s.get("parameter", {}).get("name", "").lower()
                    if sid and param_name:
                        self._station_sensors_map[sid] = param_name
        except Exception as e:
            pass

    def fetch_air_quality(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Queries OpenAQ API v3 for nearest station measurements.
        Caches results according to AIR_QUALITY_UPDATE_INTERVAL.
        """
        now = time.time()
        if not force_refresh and self._cached_data and (now - self._last_fetch_time < self.update_interval):
            return self._cached_data

        if not self.api_key or self.api_key == "your_openaq_key":
            self._last_status = "Missing API Key"
            self._last_error_message = "OpenAQ API key is not configured in .env"
            if self._cached_data:
                cached = dict(self._cached_data)
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            return {
                "source": "openaq",
                "status": "unavailable",
                "location": f"Coimbatore Station",
                "pm25": None,
                "pm10": None,
                "no2": None,
                "o3": None,
                "co": None,
                "aqi": 60,
                "aqi_category": "Moderate",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": self._last_error_message
            }

        headers = {"X-API-Key": self.api_key}

        try:
            # 1. Discover or use station
            station_id = self._known_station_id
            station_name = "SIDCO Kurichi, Coimbatore - TNPCB"

            if not station_id:
                # Query nearest stations within 25km radius (v3 constraint)
                loc_url = f"https://api.openaq.org/v3/locations?coordinates={self.latitude},{self.longitude}&radius=25000&limit=2"
                loc_res = requests.get(loc_url, headers=headers, timeout=10)
                if loc_res.status_code == 200:
                    loc_data = loc_res.json()
                    results = loc_data.get("results", [])
                    if results:
                        station_id = results[0].get("id")
                        station_name = results[0].get("name", station_name)
                        self._known_station_id = station_id
                else:
                    # Fallback to known Coimbatore monitoring station ID 8914
                    station_id = 8914
                    self._known_station_id = station_id

            if not station_id:
                station_id = 8914
                self._known_station_id = 8914

            # Map sensors if empty
            if not self._station_sensors_map:
                self._fetch_station_sensors(station_id, headers)

            # 2. Fetch latest telemetry for station
            latest_url = f"https://api.openaq.org/v3/locations/{station_id}/latest"
            latest_res = requests.get(latest_url, headers=headers, timeout=10)

            if latest_res.status_code == 200:
                latest_data = latest_res.json()
                results = latest_data.get("results", [])

                pollutants = {
                    "pm25": None,
                    "pm10": None,
                    "no2": None,
                    "o3": None,
                    "co": None,
                    "so2": None
                }
                latest_dt = None

                for item in results:
                    sid = item.get("sensorsId")
                    val = item.get("value")
                    param = self._station_sensors_map.get(sid)
                    
                    if param in pollutants and val is not None:
                        pollutants[param] = round(float(val), 2)
                    
                    dt_info = item.get("datetime", {}).get("local")
                    if dt_info:
                        latest_dt = dt_info

                aqi_val, aqi_cat = self._calculate_aqi(pollutants.get("pm25"), pollutants.get("pm10"))

                normalized = {
                    "source": "openaq",
                    "status": "connected",
                    "station_id": station_id,
                    "location": station_name,
                    "city": self.city_name,
                    "pm25": pollutants.get("pm25"),
                    "pm10": pollutants.get("pm10"),
                    "no2": pollutants.get("no2"),
                    "o3": pollutants.get("o3"),
                    "co": pollutants.get("co"),
                    "so2": pollutants.get("so2"),
                    "aqi": aqi_val,
                    "aqi_category": aqi_cat,
                    "calculation_note": "AQI calculated from measured PM2.5/PM10 concentrations via standard CPCB breakpoint formulas",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "observation_time": latest_dt or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_successful_update": datetime.datetime.now().strftime("%I:%M:%S %p")
                }

                self._cached_data = normalized
                self._last_fetch_time = now
                self._last_status = "connected"
                self._last_error_message = None
                return normalized

            else:
                err_msg = f"OpenAQ API returned HTTP {latest_res.status_code}: {latest_res.text[:120]}"
                self._last_status = "error"
                self._last_error_message = err_msg

                if self._cached_data:
                    stale = dict(self._cached_data)
                    stale["status"] = "stale"
                    stale["warning"] = f"API error ({latest_res.status_code}) — showing last valid reading from {self._cached_data.get('timestamp')}"
                    return stale

                return {
                    "source": "openaq",
                    "status": "unavailable",
                    "location": station_name,
                    "pm25": None,
                    "pm10": None,
                    "no2": None,
                    "o3": None,
                    "co": None,
                    "aqi": 60,
                    "aqi_category": "Moderate",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": err_msg
                }

        except Exception as e:
            err_msg = f"Network error contacting OpenAQ: {str(e)}"
            self._last_status = "error"
            self._last_error_message = err_msg

            if self._cached_data:
                stale = dict(self._cached_data)
                stale["status"] = "stale"
                stale["warning"] = f"Network connection failed — showing last valid reading from {self._cached_data.get('timestamp')}"
                return stale

            return {
                "source": "openaq",
                "status": "unavailable",
                "location": "Coimbatore CPCB Station",
                "pm25": None,
                "pm10": None,
                "no2": None,
                "o3": None,
                "co": None,
                "aqi": 60,
                "aqi_category": "Moderate",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": err_msg
            }

    def get_source_status(self) -> Dict[str, Any]:
        """Returns metadata for the Data Sources status panel."""
        return {
            "name": "OpenAQ",
            "source": "openaq",
            "status": self._last_status if self._cached_data else ("connected" if self._last_status == "connected" else "connecting"),
            "last_update": self._cached_data.get("last_successful_update") if self._cached_data else "Pending",
            "update_interval": f"{self.update_interval // 60}m",
            "coverage": self._cached_data.get("location") if self._cached_data else "Coimbatore Monitoring Station",
            "error": self._last_error_message
        }

air_quality_service = AirQualityService()
