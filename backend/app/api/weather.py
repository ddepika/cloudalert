from fastapi import APIRouter, HTTPException
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Complete list of cloudburst-prone districts across all states
DISTRICTS = {
    # Uttarakhand (5 districts)
    "uttarkashi": {"lat": 30.7295, "lon": 78.4456, "state": "Uttarakhand", "name": "Uttarkashi"},
    "chamoli": {"lat": 30.4183, "lon": 79.3301, "state": "Uttarakhand", "name": "Chamoli"},
    "rudraprayag": {"lat": 30.2834, "lon": 78.9775, "state": "Uttarakhand", "name": "Rudraprayag"},
    "bageshwar": {"lat": 29.8497, "lon": 79.7714, "state": "Uttarakhand", "name": "Bageshwar"},
    "pithoragarh": {"lat": 29.5828, "lon": 80.2188, "state": "Uttarakhand", "name": "Pithoragarh"},
    
    # Himachal Pradesh (7 districts)
    "mandi": {"lat": 31.7085, "lon": 76.9312, "state": "Himachal Pradesh", "name": "Mandi"},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "state": "Himachal Pradesh", "name": "Shimla"},
    "chamba": {"lat": 32.5555, "lon": 76.1301, "state": "Himachal Pradesh", "name": "Chamba"},
    "kullu": {"lat": 31.9581, "lon": 77.1082, "state": "Himachal Pradesh", "name": "Kullu"},
    "sirmaur": {"lat": 30.6573, "lon": 77.4462, "state": "Himachal Pradesh", "name": "Sirmaur"},
    "kangra": {"lat": 32.1103, "lon": 76.2752, "state": "Himachal Pradesh", "name": "Kangra"},
    "kinnaur": {"lat": 31.5552, "lon": 78.5422, "state": "Himachal Pradesh", "name": "Kinnaur"},
    
    # Jammu & Kashmir (8 districts)
    "anantnag": {"lat": 33.7345, "lon": 75.1584, "state": "Jammu & Kashmir", "name": "Anantnag"},
    "kulgam": {"lat": 33.6444, "lon": 75.0201, "state": "Jammu & Kashmir", "name": "Kulgam"},
    "ganderbal": {"lat": 34.2268, "lon": 74.9297, "state": "Jammu & Kashmir", "name": "Ganderbal"},
    "kishtwar": {"lat": 33.3139, "lon": 75.7670, "state": "Jammu & Kashmir", "name": "Kishtwar"},
    "doda": {"lat": 33.1441, "lon": 75.5472, "state": "Jammu & Kashmir", "name": "Doda"},
    "ramban": {"lat": 33.2415, "lon": 75.2252, "state": "Jammu & Kashmir", "name": "Ramban"},
    "reasi": {"lat": 33.0815, "lon": 74.8307, "state": "Jammu & Kashmir", "name": "Reasi"},
    "udhampur": {"lat": 32.9256, "lon": 75.1414, "state": "Jammu & Kashmir", "name": "Udhampur"}
}

@router.get("/districts")
async def get_all_districts():
    return {
        "total": len(DISTRICTS),
        "districts": [
            {"name": info["name"], "value": k, "lat": info["lat"], "lon": info["lon"], "state": info["state"]}
            for k, info in DISTRICTS.items()
        ]
    }

@router.get("/states")
async def get_states():
    states_dict = {}
    for district, info in DISTRICTS.items():
        state = info["state"]
        if state not in states_dict:
            states_dict[state] = []
        states_dict[state].append(info["name"])
    
    return {"states": [{"name": k, "districts": v} for k, v in states_dict.items()]}

@router.get("/live/{district}")
async def get_live_weather(district: str):
    if district.lower() not in DISTRICTS:
        raise HTTPException(status_code=404, detail="District not found")
    
    coords = DISTRICTS[district.lower()]
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": coords["lat"],
        "lon": coords["lon"],
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "district": coords["name"],
            "district_key": district,
            "state": coords["state"],
            "timestamp": datetime.now().isoformat(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"]["deg"],
            "cloud_cover": data["clouds"]["all"],
            "rainfall_1h": data.get("rain", {}).get("1h", 0),
            "rainfall_3h": data.get("rain", {}).get("3h", 0)
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}")

@router.get("/state/{state}")
async def get_state_weather(state: str):
    results = {}
    for district, info in DISTRICTS.items():
        if info["state"].lower() == state.lower():
            try:
                weather = await get_live_weather(district)
                results[district] = weather
            except HTTPException:
                results[district] = {"error": "Failed to fetch data"}
    return {"state": state, "districts": results}

@router.get("/all-districts")
async def get_all_districts_weather():
    results = {}
    for district in DISTRICTS.keys():
        try:
            results[district] = await get_live_weather(district)
        except HTTPException:
            results[district] = {"error": "Failed to fetch data"}
    return results
