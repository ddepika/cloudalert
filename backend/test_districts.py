import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("="*70)
print(" COMPREHENSIVE DISTRICT WEATHER DATA")
print("="*70)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# All 20 districts across 3 states
districts = {
    "Uttarakhand": ["uttarkashi", "chamoli", "rudraprayag", "bageshwar", "pithoragarh"],
    "Himachal Pradesh": ["mandi", "shimla", "chamba", "kullu", "sirmaur", "kangra", "kinnaur"],
    "Jammu & Kashmir": ["anantnag", "kulgam", "ganderbal", "kishtwar", "doda", "ramban", "reasi", "udhampur"]
}

all_weather_data = []

for state, district_list in districts.items():
    print(f"\n{state}")
    print("-"*50)
    
    for district in district_list:
        try:
            response = requests.get(f"{BASE_URL}/api/weather/live/{district}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_info = {
                    "state": state,
                    "district": district,
                    "temperature": data.get("temperature"),
                    "humidity": data.get("humidity"),
                    "pressure": data.get("pressure"),
                    "wind_speed": data.get("wind_speed"),
                    "cloud_cover": data.get("cloud_cover")
                }
                all_weather_data.append(weather_info)
                print(f"  {district.title():15} | Temp: {data['temperature']:5.1f}°C | Humidity: {data['humidity']:3}% | Wind: {data['wind_speed']:.1f} m/s")
            else:
                print(f"  {district.title():15} | ERROR: {response.status_code}")
        except Exception as e:
            print(f"  {district.title():15} | ERROR: {str(e)[:30]}")

print("\n" + "="*70)
print(" WEATHER STATISTICS")
print("="*70)

if all_weather_data:
    temps = [w["temperature"] for w in all_weather_data if w["temperature"]]
    humidities = [w["humidity"] for w in all_weather_data if w["humidity"]]
    winds = [w["wind_speed"] for w in all_weather_data if w["wind_speed"]]
    
    print(f"Temperature Range: {min(temps):.1f}°C to {max(temps):.1f}°C")
    print(f"Average Temperature: {sum(temps)/len(temps):.1f}°C")
    print(f"Humidity Range: {min(humidities)}% to {max(humidities)}%")
    print(f"Average Humidity: {sum(humidities)/len(humidities):.0f}%")
    print(f"Wind Speed Range: {min(winds):.1f} to {max(winds):.1f} m/s")

print("\n" + "="*70)
print(" IMD RAINFALL ANALYSIS - ALL DISTRICTS")
print("="*70)

# Test IMD data for key districts
key_districts = ["uttarkashi", "chamoli", "rudraprayag", "mandi", "anantnag"]

for district in key_districts:
    try:
        response = requests.get(f"{BASE_URL}/api/imd/rainfall/{district}?start_year=2023&end_year=2025", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{district.title()}:")
            if "monthly_rainfall" in data:
                for year, months in data["monthly_rainfall"].items():
                    if months:
                        total = sum(months.values())
                        print(f"  {year}: Total {total:.1f} mm")
        else:
            print(f"\n{district.title()}: Data not available")
    except Exception as e:
        print(f"\n{district.title()}: Error - {str(e)[:50]}")

print("\n" + "="*70)
print(" CLOUDBURST RISK ASSESSMENT")
print("="*70)

for district in key_districts[:3]:
    try:
        response = requests.get(f"{BASE_URL}/api/imd/cloudburst-risk?district={district}&start_year=2023&end_year=2025", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{district.title()}:")
            print(f"  Cloudburst Events (2023-2025): {data.get('cloudburst_events', 0)}")
            print(f"  Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"  Risk Score: {data.get('risk_score', 0)}%")
    except Exception as e:
        print(f"\n{district.title()}: Error - {str(e)[:50]}")

print("\n" + "="*70)
print(" TEST COMPLETED")
print("="*70)

# Save to file
with open("district_weather_data.json", "w") as f:
    json.dump(all_weather_data, f, indent=2)
print("Weather data saved to: district_weather_data.json")
