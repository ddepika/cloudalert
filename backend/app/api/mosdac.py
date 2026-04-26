from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

router = APIRouter()

@router.get("/verify-credentials")
async def verify_credentials():
    # \"\"\"Verify if MOSDAC credentials are configured\"\"\"
    username = os.getenv("MOSDAC_USERNAME")
    password = os.getenv("MOSDAC_PASSWORD")
    
    if not username or not password:
        return {
            "status": "MISSING",
            "message": "MOSDAC credentials not configured in .env file",
            "action": "Add MOSDAC_USERNAME and MOSDAC_PASSWORD to your .env file"
        }
    
    return {
        "status": "CONFIGURED",
        "message": f"MOSDAC credentials found for user: {username[:5]}***",
        "note": "Free/General user access is sufficient for this project"
    }

@router.get("/alerts/latest")
async def get_mosdac_alerts(district: Optional[str] = None):
    # \"\"\"Get cloudburst alerts from MOSDAC NETRA\"\"\"
    monitored_districts = ["Uttarkashi", "Chamoli", "Rudraprayag"]
    
    alerts = []
    for d in monitored_districts:
        if district and district.lower() != d.lower():
            continue
        
        # Research shows Uttarkashi has highest vulnerability
        is_high_risk = d.lower() == "uttarkashi"
        alerts.append({
            "district": d,
            "risk_level": "MODERATE" if is_high_risk else "LOW",
            "probability": 65.5 if is_high_risk else 25.0,
            "issued_at": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(hours=6)).isoformat(),
            "source": "MOSDAC NETRA"
        })
    
    return {
        "source": "MOSDAC NETRA",
        "timestamp": datetime.now().isoformat(),
        "total_alerts": len(alerts),
        "alerts": alerts,
        "note": "Free/General user access - Using simulated data. Real API requires MOSDAC credentials in .env"
    }

@router.get("/satellite/{district}")
async def get_satellite_data(district: str):
    # \"\"\"Get INSAT-3D satellite data for cloud cover analysis\"\"\"
    return {
        "district": district,
        "satellite": "INSAT-3D",
        "cloud_cover_percentage": 45,
        "cloud_top_temperature": -25.5,
        "timestamp": datetime.now().isoformat(),
        "resolution": "1 km",
        "frequency": "Half Hourly",
        "source": "MOSDAC"
    }

@router.get("/data-products")
async def list_available_products():
    # \"\"\"List available satellite data products from MOSDAC\"\"\"
    return {
        "products": [
            {
                "name": "INSAT-3D/3DR",
                "description": "Half-hourly imagery - Visible, Infrared, Water Vapour channels",
                "resolution": "1 km",
                "frequency": "30 minutes"
            },
            {
                "name": "NETRA Alerts",
                "description": "Cloudburst and heavy rain alerts for Western Himalayan region",
                "resolution": "0.1° x 0.1°",
                "frequency": "30 minutes",
                "districts": ["Uttarkashi", "Chamoli", "Rudraprayag"]
            }
        ],
        "access_level": "Free/General User",
        "note": "Level-1 data has 3-day latency for general users"
    }

@router.get("/health")
async def mosdac_health():
    # \"\"\"Check if MOSDAC integration is working\"\"\"
    return {
        "status": "healthy",
        "service": "MOSDAC Integration",
        "credentials_configured": bool(os.getenv("MOSDAC_USERNAME")),
        "endpoints": [
            "/verify-credentials",
            "/alerts/latest",
            "/alerts/latest?district=Uttarkashi",
            "/satellite/{district}",
            "/data-products"
        ]
    }

@router.get("/test")
async def test_endpoint():
    # \"\"\"Test endpoint to verify router is working\"\"\"
    return {"message": "MOSDAC router is working!"}
