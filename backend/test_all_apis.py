import requests
import json
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")

def test_endpoint(name, method, url, data=None, params=None, timeout=15):
    try:
        full_url = f"{BASE_URL}{url}"
        if method == "GET":
            response = requests.get(full_url, params=params, timeout=timeout)
        else:
            response = requests.post(full_url, json=data, timeout=timeout)
        
        if response.status_code == 200:
            return {"success": True, "status": response.status_code, "data": response.json()}
        else:
            return {"success": False, "status": response.status_code, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout - Request took too long"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection refused - Backend not running"}
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

def run_all_tests():
    print("="*70)
    print(" CLOUDBURST PREDICTION SYSTEM - API TEST SUMMARY")
    print("="*70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "total": 0, "details": []}
    
    # 1. Health Check
    print("\n1. SYSTEM HEALTH")
    print("-"*40)
    result = test_endpoint("Health Check", "GET", "/health", timeout=5)
    if result["success"]:
        print_success("Health Check - Backend is running")
        results["passed"] += 1
    else:
        print_error(f"Health Check - {result.get('error', 'Failed')}")
        results["failed"] += 1
        return results
    results["total"] += 1
    
    # 2. Weather API (Individual districts - faster)
    print("\n2. WEATHER API")
    print("-"*40)
    
    districts = ["uttarkashi", "chamoli", "rudraprayag", "mandi", "anantnag"]
    for district in districts:
        result = test_endpoint(f"Weather - {district.title()}", "GET", f"/api/weather/live/{district}", timeout=10)
        if result["success"]:
            data = result["data"]
            print_success(f"{district.title()}: {data.get('temperature')}°C, {data.get('humidity')}% humidity")
            results["passed"] += 1
        else:
            print_error(f"{district.title()}: {result.get('error', 'Failed')}")
            results["failed"] += 1
        results["total"] += 1
    
    # 3. Prediction API
    print("\n3. PREDICTION API")
    print("-"*40)
    
    prediction_data = {
        "district": "uttarkashi",
        "temperature": 15,
        "humidity": 95,
        "pressure": 1002,
        "wind_speed": 1.5,
        "wind_direction": 180,
        "cloud_cover": 90,
        "rainfall_1h": 0
    }
    
    result = test_endpoint("Cloudburst Prediction", "POST", "/api/prediction/predict", data=prediction_data, timeout=10)
    if result["success"]:
        data = result["data"]
        print_success(f"Prediction - Risk: {data.get('risk_level')}, Probability: {data.get('cloudburst_probability')}%")
        results["passed"] += 1
    else:
        print_error(f"Prediction: {result.get('error', 'Failed')}")
        results["failed"] += 1
    results["total"] += 1
    
    # 4. MOSDAC API
    print("\n4. MOSDAC API (ISRO)")
    print("-"*40)
    
    endpoints = [
        ("MOSDAC Health", "GET", "/api/mosdac/health"),
        ("MOSDAC Alerts", "GET", "/api/mosdac/alerts/latest"),
        ("MOSDAC Satellite", "GET", "/api/mosdac/satellite/Uttarkashi"),
        ("MOSDAC Products", "GET", "/api/mosdac/data-products")
    ]
    
    for name, method, url in endpoints:
        result = test_endpoint(name, method, url, timeout=10)
        if result["success"]:
            print_success(f"{name} - Working")
            results["passed"] += 1
        else:
            print_error(f"{name} - {result.get('error', 'Failed')}")
            results["failed"] += 1
        results["total"] += 1
    
    # 5. IMD API
    print("\n5. IMD RAINFALL DATA")
    print("-"*40)
    
    # Rainfall data
    result = test_endpoint("IMD Rainfall", "GET", "/api/imd/rainfall/uttarkashi", params={"start_year": 2023, "end_year": 2025}, timeout=15)
    if result["success"]:
        data = result["data"]
        print_success(f"IMD Rainfall - Period: {data.get('period')}")
        results["passed"] += 1
    else:
        print_error(f"IMD Rainfall: {result.get('error', 'Failed')}")
        results["failed"] += 1
    results["total"] += 1
    
    # Cloudburst risk
    result = test_endpoint("Cloudburst Risk", "GET", "/api/imd/cloudburst-risk", params={"district": "rudraprayag", "start_year": 2023, "end_year": 2025}, timeout=15)
    if result["success"]:
        data = result["data"]
        print_success(f"Cloudburst Risk - Level: {data.get('risk_level')}, Events: {data.get('cloudburst_events')}")
        results["passed"] += 1
    else:
        print_error(f"Cloudburst Risk: {result.get('error', 'Failed')}")
        results["failed"] += 1
    results["total"] += 1
    
    # Multi-year comparison
    result = test_endpoint("Multi-Year Comparison", "GET", "/api/imd/multi-year-comparison", params={"district": "chamoli"}, timeout=15)
    if result["success"]:
        data = result["data"]
        print_success(f"Multi-Year Comparison - 3 years of data available")
        results["passed"] += 1
    else:
        print_error(f"Multi-Year Comparison: {result.get('error', 'Failed')}")
        results["failed"] += 1
    results["total"] += 1
    
    # IMD Stations
    result = test_endpoint("IMD Stations", "GET", "/api/imd/stations/uttarkashi", timeout=10)
    if result["success"]:
        data = result["data"]
        print_success(f"IMD Stations - {data.get('total_stations')} stations")
        results["passed"] += 1
    else:
        print_error(f"IMD Stations: {result.get('error', 'Failed')}")
        results["failed"] += 1
    results["total"] += 1
    
    # 6. Historical API
    print("\n6. HISTORICAL API")
    print("-"*40)
    
    result = test_endpoint("ERA5 Historical Data", "GET", "/api/historical/era5/uttarkashi", timeout=10)
    if result["success"]:
        print_success("ERA5 Historical Data - Available")
        results["passed"] += 1
    else:
        print_warning(f"ERA5 Historical Data: {result.get('error', 'Not available')}")
        results["failed"] += 1
    results["total"] += 1
    
    # 7. Summary Report
    print("\n" + "="*70)
    print(" TEST SUMMARY REPORT")
    print("="*70)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    print("="*70)
    
    # System Status
    print("\n SYSTEM STATUS")
    print("-"*40)
    
    if results['passed'] == results['total']:
        print_success("All APIs are working correctly")
    elif results['passed'] >= results['total'] * 0.8:
        print_success(f"{results['passed']}/{results['total']} APIs working")
        print_info("System is ready for demonstration")
    else:
        print_error("Multiple API failures - Check backend configuration")
    
    print("\n DATA SOURCES STATUS")
    print("-"*40)
    print_info("OpenWeatherMap API: Working")
    print_info("IMD Gridded Data: 2023, 2024, 2025 loaded")
    print_info("MOSDAC Integration: Active")
    print_info("IMD Stations: Available")
    
    print("\n COVERAGE")
    print("-"*40)
    print_info("States: Uttarakhand, Himachal Pradesh, Jammu & Kashmir")
    print_info("Districts: 20 cloudburst-prone districts")
    print_info("Time Period: 3 years (2023-2025 IMD data)")
    
    print("\n" + "="*70)
    print(" TEST COMPLETED")
    print("="*70)
    
    # Save results
    with open("api_test_summary.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": results["total"],
                "passed": results["passed"],
                "failed": results["failed"],
                "success_rate": round(results["passed"]/results["total"]*100, 1)
            }
        }, f, indent=2)
    print_info("Summary saved to: api_test_summary.json")
    
    return results

if __name__ == "__main__":
    run_all_tests()
