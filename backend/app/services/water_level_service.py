"""
Water Level Simulation Service
------------------------------
Water-level data is simulated because a reliable authorized real-time water-level source is not currently integrated.
This module models a physical hydrological basin where water level smoothly drifts around a baseline
and responds dynamically to observed rainfall from OpenWeather.
"""

import datetime
from typing import Dict, Any

class WaterLevelService:
    def __init__(self):
        # Base levels in meters for different zone types
        self.zone_baselines = {
            "river-zone": 1.4,      # Closer to river bed
            "valankulam-lake": 1.3, # Smart city lake promenade
            "ukkadam-junction": 1.2, # Periyakulam lake basin
            "perur-corridor": 1.3,  # Noyyal river riparian bank
            "residential-zone": 0.8,
            "industrial-area": 0.9,
            "central-junction": 0.7,
            "railway-station": 0.7,
            "airport-road": 0.6,
            "city-hospital": 0.6,
            "bus-terminal": 0.7,
            "tidel-park": 0.6,
            "saravanampatti": 0.7,
            "singanallur-junction": 0.9,
            "ramanathapuram": 0.8
        }
        # In-memory tracking of recent levels per location
        self._current_levels: Dict[str, float] = {}

    def get_water_level(self, location_id: str, current_rainfall: float = 0.0, is_demo_scenario: str = None) -> Dict[str, Any]:
        """
        Calculates a realistic hydrological water level responding to rainfall.
        In demo scenario (e.g. heavy_rain), models sustained accumulation.
        """
        baseline = self.zone_baselines.get(location_id, 0.8)
        current = self._current_levels.get(location_id, baseline)

        if is_demo_scenario == "heavy_rain":
            # Rapid surge during heavy rain simulation
            target = baseline + (current_rainfall * 0.04) + (1.5 if location_id == "river-zone" else 0.8)
            # Smoothly transition towards target
            new_level = current + (target - current) * 0.35
            new_level = min(5.5, max(1.8, new_level))
        elif is_demo_scenario == "rush_hour":
            new_level = baseline + 0.1
        else:
            # LIVE MODE or normal simulation:
            # Water level directly correlates with actual measured rainfall (mm/h)
            if current_rainfall > 0.0:
                # Rainfall adds runoff into water level
                rain_effect = current_rainfall * 0.025
                target = baseline + rain_effect
            else:
                # Drainage effect slowly recedes towards baseline
                target = baseline

            # Smooth gradual movement (simulating drainage/runoff dynamics)
            delta = (target - current) * 0.2
            new_level = current + delta
            # Ensure it stays within physical limits
            new_level = max(0.4, min(4.5, round(new_level, 2)))

        self._current_levels[location_id] = round(new_level, 2)

        return {
            "source": "simulation",
            "location_id": location_id,
            "water_level": round(new_level, 2),
            "unit": "meters",
            "is_simulated": True,
            "note": "Water-level data is simulated because a reliable authorized real-time water-level source is not currently integrated.",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

water_level_service = WaterLevelService()
