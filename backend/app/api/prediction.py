from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import numpy as np
import os
import tensorflow as tf
from typing import Optional

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
    # Simple rule-based calculation
    # High humidity + low pressure + low wind speed = cloudburst risk
    
    humidity_score = request.humidity / 100
    pressure_score = max(0, (1013 - request.pressure) / 30)
    wind_score = max(0, (5 - request.wind_speed) / 10)
    cloud_score = request.cloud_cover / 100
    
    # Weighted combination
    probability = (humidity_score * 0.4) + (pressure_score * 0.3) + (wind_score * 0.2) + (cloud_score * 0.1)
    probability = min(max(probability, 0), 1)  # Clamp between 0 and 1
    
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
