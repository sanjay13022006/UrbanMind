"""
TomTom Traffic API Integration Service
--------------------------------------
Retrieves real-time traffic flow metrics (current speed, free-flow speed, travel time, delay)
for configured urban coordinates using TomTom Traffic Flow API.
Calculates congestion percentages and traffic condition categories.
Provides per-location caching and resilient error handling.
"""

import time
import datetime
import requests
from typing import Dict, Any, Optional
from app import config

class TrafficService:
    def __init__(self):
        self.api_key = config.TOMTOM_API_KEY
        self.update_interval = config.TRAFFIC_UPDATE_INTERVAL  # seconds

        # Cache per location_id: { "data": ..., "fetch_time": ... }
        self._location_cache: Dict[str, Dict[str, Any]] = {}
        self._last_status: str = "Uninitialized"
        self._last_error_message: Optional[str] = None
        self._last_successful_update: Optional[str] = None

    def _determine_traffic_level(self, congestion_percentage: float, speed: float) -> str:
        """
        Thresholds:
          0 - 20%  -> Normal (Low)
          21 - 40% -> Moderate
          41 - 60% -> High
          61%+     -> Critical
        """
        if congestion_percentage >= 60.0 or speed < 12.0:
            return "Critical"
        elif congestion_percentage >= 40.0 or speed < 22.0:
            return "High"
        elif congestion_percentage >= 20.0 or speed < 35.0:
            return "Moderate"
        else:
            return "Low"

    def fetch_traffic_for_point(self, location_id: str, lat: float, lng: float, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Retrieves real-time traffic flow for specific location coordinates from TomTom.
        """
        now = time.time()
        cached_entry = self._location_cache.get(location_id)

        if not force_refresh and cached_entry and (now - cached_entry["fetch_time"] < self.update_interval):
            return cached_entry["data"]

        if not self.api_key or self.api_key == "your_tomtom_key":
            self._last_status = "Missing API Key"
            self._last_error_message = "TomTom API key is not configured in .env"
            if cached_entry:
                cached = dict(cached_entry["data"])
                cached["status"] = "stale"
                cached["warning"] = self._last_error_message
                return cached
            return {
                "source": "tomtom",
                "status": "unavailable",
                "location_id": location_id,
                "current_speed": 35.0,
                "free_flow_speed": 45.0,
                "delay_seconds": 0,
                "congestion_percentage": 22.0,
                "traffic_condition": "Moderate",
                "traffic_level": "Moderate",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": self._last_error_message
            }

        url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        params = {
            "point": f"{lat},{lng}",
            "key": self.api_key,
            "unit": "KMPH"
        }

        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                raw = res.json()
                flow = raw.get("flowSegmentData", {})

                current_speed = round(float(flow.get("currentSpeed", 30.0)), 1)
                free_flow_speed = round(float(flow.get("freeFlowSpeed", max(35.0, current_speed))), 1)
                current_travel_time = int(flow.get("currentTravelTime", 0))
                free_flow_travel_time = int(flow.get("freeFlowTravelTime", 0))
                confidence = round(float(flow.get("confidence", 0.9)), 3)
                road_closure = bool(flow.get("roadClosure", False))

                delay_seconds = max(0, current_travel_time - free_flow_travel_time)

                if free_flow_speed > 0:
                    congestion_pct = max(0.0, (free_flow_speed - current_speed) / free_flow_speed * 100.0)
                else:
                    congestion_pct = 0.0

                congestion_pct = round(congestion_pct, 1)
                traffic_level = self._determine_traffic_level(congestion_pct, current_speed)

                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                update_time_str = datetime.datetime.now().strftime("%I:%M:%S %p")

                normalized = {
                    "source": "tomtom",
                    "status": "connected",
                    "location_id": location_id,
                    "latitude": lat,
                    "longitude": lng,
                    "current_speed": current_speed,
                    "free_flow_speed": free_flow_speed,
                    "current_travel_time": current_travel_time,
                    "free_flow_travel_time": free_flow_travel_time,
                    "delay_seconds": delay_seconds,
                    "congestion_percentage": congestion_pct,
                    "traffic_condition": traffic_level,
                    "traffic_level": traffic_level,
                    "road_closure": road_closure,
                    "tomtom_confidence": confidence,
                    "timestamp": now_str,
                    "last_successful_update": update_time_str
                }

                self._location_cache[location_id] = {
                    "data": normalized,
                    "fetch_time": now
                }
                self._last_status = "connected"
                self._last_error_message = None
                self._last_successful_update = update_time_str
                return normalized

            else:
                err_msg = f"TomTom API returned HTTP {res.status_code}: {res.text[:120]}"
                self._last_status = "error"
                self._last_error_message = err_msg

                if cached_entry:
                    stale = dict(cached_entry["data"])
                    stale["status"] = "stale"
                    stale["warning"] = f"Traffic API error ({res.status_code}) — showing last valid observation from {stale.get('timestamp')}"
                    return stale

                return {
                    "source": "tomtom",
                    "status": "unavailable",
                    "location_id": location_id,
                    "current_speed": 30.0,
                    "free_flow_speed": 40.0,
                    "delay_seconds": 0,
                    "congestion_percentage": 25.0,
                    "traffic_condition": "Moderate",
                    "traffic_level": "Moderate",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": err_msg
                }

        except Exception as e:
            err_msg = f"Network error contacting TomTom Traffic: {str(e)}"
            self._last_status = "error"
            self._last_error_message = err_msg

            if cached_entry:
                stale = dict(cached_entry["data"])
                stale["status"] = "stale"
                stale["warning"] = f"Network connection failed — showing last valid observation from {stale.get('timestamp')}"
                return stale

            return {
                "source": "tomtom",
                "status": "unavailable",
                "location_id": location_id,
                "current_speed": 30.0,
                "free_flow_speed": 40.0,
                "delay_seconds": 0,
                "congestion_percentage": 25.0,
                "traffic_condition": "Moderate",
                "traffic_level": "Moderate",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": err_msg
            }

    def get_source_status(self) -> Dict[str, Any]:
        """Returns metadata for the Data Sources status panel."""
        return {
            "name": "TomTom Traffic",
            "source": "tomtom",
            "status": self._last_status if self._last_successful_update else ("connected" if self._last_status == "connected" else "connecting"),
            "last_update": self._last_successful_update or "Pending",
            "update_interval": f"{self.update_interval}s",
            "coverage": "Corridor-level real-time traffic flow",
            "error": self._last_error_message
        }

traffic_service = TrafficService()
