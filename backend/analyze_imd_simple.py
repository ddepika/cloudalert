import xarray as xr
import os

print('='*60)
print('IMD Data Analysis - Uttarakhand 2023-2025')
print('='*60)

districts = {
    'uttarkashi': {'lat': 30.73, 'lon': 78.45},
    'chamoli': {'lat': 30.42, 'lon': 79.33},
    'rudraprayag': {'lat': 30.28, 'lon': 78.98}
}

years = [2023, 2024, 2025]

print('\nRainfall Statistics (mm per year):')
print('-'*60)
print(f'{"District":15} {"Year":5} {"Total (mm)":12} {"Max (mm)":10} {"Cloudburst Days":15}')
print('-'*60)

for district, coords in districts.items():
    for year in years:
        file_path = f'data/imd/{year}/RF25_ind{year}_rfp25.nc'
        
        if os.path.exists(file_path):
            ds = xr.open_dataset(file_path, engine='netcdf4')
            point = ds.sel(
                LATITUDE=coords['lat'],
                LONGITUDE=coords['lon'],
                method='nearest'
            )
            rainfall = point.RAINFALL.values
            
            total = rainfall.sum()
            max_rain = rainfall.max()
            cloudburst = (rainfall > 100).sum()
            
            print(f'{district:15} {year:5} {total:12.1f} {max_rain:10.1f} {cloudburst:15}')
            ds.close()
        else:
            print(f'{district:15} {year:5} {"N/A":12} {"N/A":10} {"N/A":15}')

print('\n' + '='*60)
print('Analysis Complete')
print('='*60)
