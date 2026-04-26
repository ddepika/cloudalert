from fastapi import APIRouter, HTTPException
import xarray as xr
import os

router = APIRouter()

DISTRICT_COORDS = {
    "uttarkashi": {"lat": 30.73, "lon": 78.45},
    "chamoli": {"lat": 30.42, "lon": 79.33},
    "rudraprayag": {"lat": 30.28, "lon": 78.98},
    "bageshwar": {"lat": 29.85, "lon": 79.77},
    "pithoragarh": {"lat": 29.58, "lon": 80.22},
    "mandi": {"lat": 31.71, "lon": 76.93},
    "shimla": {"lat": 31.10, "lon": 77.17},
    "chamba": {"lat": 32.55, "lon": 76.13},
    "kullu": {"lat": 31.96, "lon": 77.11},
    "kangra": {"lat": 32.11, "lon": 76.28},
    "anantnag": {"lat": 33.73, "lon": 75.16},
    "kishtwar": {"lat": 33.31, "lon": 75.77}
}

@router.get("/rainfall/{district}")
async def get_rainfall_data(district: str, start_year: int = 2023, end_year: int = 2025):
    if district.lower() not in DISTRICT_COORDS:
        raise HTTPException(status_code=404, detail="District not found")
    
    result = {
        "district": district,
        "data_source": "IMD Gridded Rainfall Data",
        "period": f"{start_year}-{end_year}",
        "monthly_rainfall": {}
    }
    
    for year in range(start_year, end_year + 1):
        file_path = f"data/imd/{year}/RF25_ind{year}_rfp25.nc"
        if os.path.exists(file_path):
            ds = xr.open_dataset(file_path, engine='netcdf4')
            point = ds.sel(
                LATITUDE=DISTRICT_COORDS[district.lower()]["lat"],
                LONGITUDE=DISTRICT_COORDS[district.lower()]["lon"],
                method='nearest'
            )
            rainfall = point.RAINFALL.values
            
            days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if year == 2024:
                days_per_month[1] = 29
            
            monthly = {}
            idx = 0
            for m, days in enumerate(days_per_month, 1):
                month_rain = rainfall[idx:idx+days].sum()
                monthly[str(m)] = round(float(month_rain), 1)
                idx += days
            
            result["monthly_rainfall"][str(year)] = monthly
            ds.close()
    
    return result

@router.get("/cloudburst-risk")
async def get_cloudburst_risk(district: str, start_year: int = 2023, end_year: int = 2025):
    if district.lower() not in DISTRICT_COORDS:
        raise HTTPException(status_code=404, detail="District not found")
    
    try:
        coords = DISTRICT_COORDS[district.lower()]
        total_cloudbursts = 0
        total_days = 0
        yearly_data = []
        
        for year in range(start_year, end_year + 1):
            file_path = f"data/imd/{year}/RF25_ind{year}_rfp25.nc"
            if os.path.exists(file_path):
                ds = xr.open_dataset(file_path, engine='netcdf4')
                point = ds.sel(
                    LATITUDE=coords["lat"],
                    LONGITUDE=coords["lon"],
                    method='nearest'
                )
                rainfall = point.RAINFALL.values
                cloudbursts = int((rainfall > 100).sum())
                total_cloudbursts += cloudbursts
                total_days += len(rainfall)
                yearly_data.append({"year": year, "cloudbursts": cloudbursts})
                ds.close()
        
        if total_days == 0:
            return {"district": district, "error": "No data available"}
        
        risk_score = (total_cloudbursts / total_days) * 100
        
        if risk_score > 1.0:
            risk_level = "HIGH"
            message = "High cloudburst risk zone - Immediate monitoring required"
        elif risk_score > 0.5:
            risk_level = "MEDIUM"
            message = "Medium cloudburst risk - Regular monitoring advised"
        else:
            risk_level = "LOW"
            message = "Low cloudburst risk - Normal conditions"
        
        return {
            "district": district,
            "period": f"{start_year}-{end_year}",
            "total_days": total_days,
            "cloudburst_events": total_cloudbursts,
            "cloudburst_frequency": round(risk_score, 4),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "message": message,
            "yearly_breakdown": yearly_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@router.get("/multi-year-comparison")
async def multi_year_comparison(district: str):
    if district.lower() not in DISTRICT_COORDS:
        raise HTTPException(status_code=404, detail="District not found")
    
    coords = DISTRICT_COORDS[district.lower()]
    comparison = {}
    
    for year in [2023, 2024, 2025]:
        file_path = f"data/imd/{year}/RF25_ind{year}_rfp25.nc"
        if os.path.exists(file_path):
            ds = xr.open_dataset(file_path, engine='netcdf4')
            point = ds.sel(
                LATITUDE=coords["lat"],
                LONGITUDE=coords["lon"],
                method='nearest'
            )
            rainfall = point.RAINFALL.values
            comparison[str(year)] = {
                "total_rainfall": round(float(rainfall.sum()), 1),
                "max_24h": round(float(rainfall.max()), 1),
                "cloudburst_events": int((rainfall > 100).sum())
            }
            ds.close()
    
    return {"district": district, "yearly_comparison": comparison}

@router.get("/stations/{district}")
async def get_stations(district: str):
    stations = {
        "uttarkashi": ["Bhatwari", "Chinyalisaur", "Dunda", "Gangotri", "Harsil"],
        "chamoli": ["Badrinath", "Gopeshwar", "Joshimath", "Karnaprayag", "Nandaprayag"],
        "rudraprayag": ["Agastyamuni", "Guptakashi", "Kedarnath", "Rudraprayag", "Tilwara"],
        "mandi": ["Pandoh", "Sundernagar", "Karsog"],
        "shimla": ["Kufri", "Narkanda", "Theog"],
        "anantnag": ["Pahalgam", "Kokernag", "Verinag"]
    }
    
    if district.lower() not in stations:
        return {
            "district": district,
            "total_stations": 0,
            "stations": [],
            "message": "Station data not available for this district",
            "data_types": ["Temperature", "Humidity", "Pressure", "Wind Speed", "Rainfall"],
            "data_frequency": "Hourly"
        }
    
    return {
        "district": district,
        "total_stations": len(stations[district.lower()]),
        "stations": stations[district.lower()],
        "data_types": ["Temperature", "Humidity", "Pressure", "Wind Speed", "Rainfall"],
        "data_frequency": "Hourly"
    }
