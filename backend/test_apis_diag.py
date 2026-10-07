import requests
import os
import sys
import json
from dotenv import load_dotenv

# Ensure utf-8 output
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(".env")
ow_key = os.getenv("OPENWEATHER_API_KEY")
aq_key = os.getenv("OPENAQ_API_KEY")
tt_key = os.getenv("TOMTOM_API_KEY")

locations = [
    ("Saibaba Colony", 11.0226, 76.9408),
    ("Railway Station", 10.9984, 76.9632),
    ("Central Junction", 11.0183, 76.9644),
    ("Airport Road", 11.0298, 77.0270),
    ("Industrial Area", 10.9425, 76.9790),
    ("Residential Zone", 11.0102, 76.9492),
    ("River Zone", 10.9950, 77.0200),
    ("Bus Terminal", 11.0195, 76.9680),
]

print("=== OPENWEATHER TEST ===")
for name, lat, lon in locations:
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": ow_key, "units": "metric"},
        timeout=10
    )
    if r.status_code == 200:
        d = r.json()
        print(f"{name} ({lat}, {lon}): temp={d['main']['temp']}, humidity={d['main']['humidity']}, rain={d.get('rain', {})}, weather={d['weather'][0]['main']}, location_name={d.get('name')}")
    else:
        print(f"{name} Error: {r.status_code}")

print("\n=== OPENAQ STATIONS TEST ===")
headers = {"X-API-Key": aq_key} if aq_key else {}
r = requests.get(
    "https://api.openaq.org/v3/locations?coordinates=11.0168,76.9558&radius=50000&limit=10",
    headers=headers,
    timeout=10
)
print("OpenAQ status:", r.status_code)
if r.status_code == 200:
    res = r.json().get("results", [])
    print(f"Found {len(res)} stations:")
    for s in res:
        coords = s.get("coordinates", {})
        print(f"  Station ID {s.get('id')}: '{s.get('name')}' at ({coords.get('latitude')}, {coords.get('longitude')})")

print("\n=== TOMTOM TRAFFIC TEST ===")
for name, lat, lon in locations[:4]:
    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    tr = requests.get(url, params={"point": f"{lat},{lon}", "key": tt_key, "unit": "KMPH"}, timeout=10)
    print(f"{name} TomTom status: {tr.status_code}")
    if tr.status_code == 200:
        flow = tr.json().get("flowSegmentData", {})
        print(f"  curSpeed={flow.get('currentSpeed')}, ffSpeed={flow.get('freeFlowSpeed')}, curTime={flow.get('currentTravelTime')}, ffTime={flow.get('freeFlowTravelTime')}, delay={flow.get('currentTravelTime', 0) - flow.get('freeFlowTravelTime', 0)}")
