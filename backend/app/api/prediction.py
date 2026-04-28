from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.services.ml_service import ml_service

router = APIRouter()

class PredictionRequest(BaseModel):
    district: str
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    wind_direction: float
    cloud_cover: float
    rainfall_1h: Optional[float] = 0
    rainfall_3h: Optional[float] = 0

class PredictionResponse(BaseModel):
    district: str
    timestamp: datetime
    cloudburst_probability: float
    risk_level: str
    warning_hours: int
    message: str

@router.post("/predict", response_model=PredictionResponse)
async def predict_cloudburst(request: PredictionRequest):
    features = {
        'temperature': request.temperature,
        'humidity': request.humidity,
        'pressure': request.pressure,
        'wind_speed': request.wind_speed,
        'cloud_cover': request.cloud_cover
    }
    
    probability = ml_service.predict(features)
    
    if probability > 0.7:
        risk_level = "HIGH"
        message = "Immediate action required - High cloudburst risk detected"
        warning_hours = 2
    elif probability > 0.4:
        risk_level = "MEDIUM"
        message = "Monitor conditions closely - Elevated risk"
        warning_hours = 4
    else:
        risk_level = "LOW"
        message = "Normal conditions - No immediate threat"
        warning_hours = 6
    
    return PredictionResponse(
        district=request.district,
        timestamp=datetime.now(),
        cloudburst_probability=round(probability * 100, 2),
        risk_level=risk_level,
        warning_hours=warning_hours,
        message=message
    )
