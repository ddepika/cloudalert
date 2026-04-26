from fastapi import APIRouter

router = APIRouter()

@router.get("/era5/{district}")
async def get_era5_data(district: str):
    return {"message": f"ERA5 data for {district} - Data available for download"}

@router.get("/mosdac/alerts")
async def get_mosdac_alerts():
    return {"message": "MOSDAC alerts - Real-time data available from ISRO"}
