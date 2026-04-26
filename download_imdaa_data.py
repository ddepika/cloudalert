import xarray as xr
import pooch
import os

print("="*60)
print("Downloading IMDAA Reanalysis Data for Uttarakhand")
print("="*60)

# Create data directory
os.makedirs("./data/imdaa", exist_ok=True)

# IMDAA sample data (India-specific, high resolution)
print("\n📥 Downloading IMDAA sample data...")

# Try multiple sources
urls = [
    "https://nimrod.iitm.ac.in/IMDAA/IMDAA_2024_sample.nc",
    "https://cloud.nimrod.iitm.ac.in/imdaa/sample.nc",
]

for url in urls:
    try:
        file_path = pooch.retrieve(
            url=url,
            known_hash=None,
            path="./data/imdaa",
            fname="imdaa_uttarakhand.nc"
        )
        print(f"✅ Downloaded from: {url}")
        break
    except Exception as e:
        print(f"⚠️ Failed from {url}: {str(e)[:50]}")

# Try to open the file
if os.path.exists("./data/imdaa/imdaa_uttarakhand.nc"):
    ds = xr.open_dataset("./data/imdaa/imdaa_uttarakhand.nc")
    print("\n✅ IMDAA Data loaded successfully!")
    print(f"Variables: {list(ds.data_vars.keys())}")
    print(f"Dimensions: {dict(ds.dims)}")
    
    # Check if Uttarakhand coordinates are available
    if 'latitude' in ds.coords:
        lat_range = ds.latitude.values
        print(f"Latitude range: {lat_range.min():.2f} to {lat_range.max():.2f}")
    if 'longitude' in ds.coords:
        lon_range = ds.longitude.values
        print(f"Longitude range: {lon_range.min():.2f} to {lon_range.max():.2f}")
else:
    print("\n❌ Could not download IMDAA data")
    print("Using alternative: Create synthetic training data for now")
    
    # Create synthetic data for testing ML pipeline
    import numpy as np
    import pandas as pd
    
    print("\n📊 Creating synthetic training data for ML pipeline...")
    dates = pd.date_range('2023-06-01', '2023-09-30', freq='6H')
    n_samples = len(dates)
    
    synthetic_data = xr.Dataset(
        {
            'temperature': (('time',), 20 + 10 * np.sin(np.arange(n_samples) / 24 * np.pi) + np.random.randn(n_samples) * 2),
            'humidity': (('time',), 60 + 20 * np.sin(np.arange(n_samples) / 12 * np.pi) + np.random.randn(n_samples) * 5),
            'pressure': (('time',), 1010 + 5 * np.sin(np.arange(n_samples) / 48 * np.pi) + np.random.randn(n_samples) * 2),
            'rainfall': (('time',), np.random.exponential(2, n_samples)),
        },
        coords={'time': dates}
    )
    
    print(f"✅ Created synthetic dataset with {n_samples} time steps")
    ds = synthetic_data

print("\n" + "="*60)
print("Data ready for model training!")
print("="*60)
ds
