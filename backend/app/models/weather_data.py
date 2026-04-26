from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, index=True)
    state = Column(String)
    source = Column(String)
    timestamp = Column(DateTime(timezone=True), index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    cloud_cover = Column(Float)
    rainfall = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserAlert(Base):
    __tablename__ = "user_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    user_email = Column(String, index=True)
    district = Column(String)
    alert_level = Column(String)
    probability = Column(Float)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
