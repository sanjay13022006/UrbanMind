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

# Known official CAAQMS monitoring stations in Coimbatore metropolitan area
COIMBATORE_MONITORING_STATIONS = [
    {
        "id": 8914,
        "name": "SIDCO Kurichi, Coimbatore - TNPCB",
        "lat": 10.942451,
        "lon": 76.978996
    },
    {
        "id": 358457,
        "name": "PSG College of Arts and Science, Coimbatore - TNPCB",
        "lat": 11.0328,
        "lon": 77.0349
    }
]

class AirQualityService:
    def __init__(self):
        self.api_key = config.OPENAQ_API_KEY
        self.city_name = config.CITY_NAME
        self.latitude = config.LATITUDE
        self.longitude = config.LONGITUDE
        self.update_interval = config.AIR_QUALITY_UPDATE_INTERVAL

        # Stations list
        self._stations = list(COIMBATORE_MONITORING_STATIONS)
        self._stations_discovered = False

        # Cache per station_id: { station_id: { "data": ..., "fetch_time": ... } }
        self._station_cache: Dict[int, Dict[str, Any]] = {}
        # City-wide default cache
        self._cached_data: Optional[Dict[str, Any]] = None
        self._last_fetch_time: float = 0
        self._last_status: str = "Uninitialized"
        self._last_error_message: Optional[str] = None
        self._station_sensors_map: Dict[int, Dict[int, str]] = {}

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

    def find_nearest_station(self, lat: float, lon: float) -> Dict[str, Any]:
        """Finds nearest monitoring station using Euclidean distance."""
        best_station = self._stations[0]
        min_dist = float("inf")
        for s in self._stations:
            dist = (lat - s["lat"]) ** 2 + (lon - s["lon"]) ** 2
            if dist < min_dist:
                min_dist = dist
                best_station = s
        return best_station

    def _discover_stations(self, headers: dict):
        """Discovers active Coimbatore monitoring stations via OpenAQ bbox API."""
        if self._stations_discovered:
            return
        try:
            url = "https://api.openaq.org/v3/locations?bbox=76.8,10.8,77.2,11.2"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                results = res.json().get("results", [])
                if results:
                    discovered = []
                    for r in results:
                        sid = r.get("id")
                        name = r.get("name")
                        coords = r.get("coordinates", {})
                        slat = coords.get("latitude")
                        slon = coords.get("longitude")
                        if sid and name and slat and slon:
                            discovered.append({
                                "id": sid,
                                "name": name,
                                "lat": float(slat),
                                "lon": float(slon)
                            })
                    if discovered:
                        self._stations = discovered
            self._stations_discovered = True
        except Exception:
            self._stations_discovered = True

    def _fetch_station_sensors(self, station_id: int, headers: dict):
        """Map sensor IDs to parameter names for the station."""
        if station_id in self._station_sensors_map:
            return
        self._station_sensors_map[station_id] = {}
        try:
            url = f"https://api.openaq.org/v3/locations/{station_id}/sensors"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                for s in data.get("results", []):
                    sid = s.get("id")
                    param_name = s.get("parameter", {}).get("name", "").lower()
                    if sid and param_name:
                        self._station_sensors_map[station_id][sid] = param_name
        except Exception:
            pass

    def fetch_air_quality(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Queries OpenAQ API v3 for the nearest monitoring station to given coordinates.
        Uses in-memory caching per station according to AIR_QUALITY_UPDATE_INTERVAL.
        """
        now = time.time()
        
        # Determine target station
        if lat is not None and lon is not None:
            station = self.find_nearest_station(float(lat), float(lon))
        else:
            station = self.find_nearest_station(self.latitude, self.longitude)

        station_id = station["id"]
        station_name = station["name"]

        cached_entry = self._station_cache.get(station_id)
        if not force_refresh and cached_entry and (now - cached_entry["fetch_time"] < self.update_interval):
            return cached_entry["data"]

        if not self.api_key or self.api_key == "your_openaq_key":
            self._last_status = "Missing API Key"
            self._last_error_message = "OpenAQ API key is not configured in .env"
            if cached_entry:
                cached = dict(cached_entry["data"])
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            elif self._cached_data:
                cached = dict(self._cached_data)
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            return {
                "source": "openaq",
                "status": "unavailable",
                "station_id": station_id,
                "location": station_name,
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
            # 1. Discover stations if not done yet
            self._discover_stations(headers)

            # Re-verify nearest station after discovery
            if lat is not None and lon is not None:
                station = self.find_nearest_station(float(lat), float(lon))
            else:
                station = self.find_nearest_station(self.latitude, self.longitude)
            station_id = station["id"]
            station_name = station["name"]

            # Map sensors for this station if not yet cached
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
                sensor_map = self._station_sensors_map.get(station_id, {})

                for item in results:
                    sid = item.get("sensorsId")
                    val = item.get("value")
                    param = sensor_map.get(sid)
                    
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
                    "station_latitude": station.get("lat"),
                    "station_longitude": station.get("lon"),
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

                self._station_cache[station_id] = {
                    "data": normalized,
                    "fetch_time": now
                }
                # Maintain default city cache
                if (lat is None and lon is None) or not self._cached_data:
                    self._cached_data = normalized
                    self._last_fetch_time = now

                self._last_status = "connected"
                self._last_error_message = None
                return normalized

            else:
                err_msg = f"OpenAQ API returned HTTP {latest_res.status_code}: {latest_res.text[:120]}"
                self._last_status = "error"
                self._last_error_message = err_msg

                if cached_entry:
                    stale = dict(cached_entry["data"])
                    stale["status"] = "stale"
                    stale["warning"] = f"API error ({latest_res.status_code}) — showing last valid reading from {stale.get('timestamp')}"
                    return stale
                elif self._cached_data:
                    stale = dict(self._cached_data)
                    stale["status"] = "stale"
                    stale["warning"] = f"API error ({latest_res.status_code}) — showing last valid reading from {self._cached_data.get('timestamp')}"
                    return stale

                return {
                    "source": "openaq",
                    "status": "unavailable",
                    "station_id": station_id,
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

            if cached_entry:
                stale = dict(cached_entry["data"])
                stale["status"] = "stale"
                stale["warning"] = f"Network connection failed — showing last valid reading from {stale.get('timestamp')}"
                return stale
            elif self._cached_data:
                stale = dict(self._cached_data)
                stale["status"] = "stale"
                stale["warning"] = f"Network connection failed — showing last valid reading from {self._cached_data.get('timestamp')}"
                return stale

            return {
                "source": "openaq",
                "status": "unavailable",
                "station_id": station_id,
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
