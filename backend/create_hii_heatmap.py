import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

print('='*60)
print('Creating HII Heat Map for Uttarakhand')
print('='*60)

# Load IMD rainfall data
ds = xr.open_dataset('data/imd/uttarakhand_rainfall_2024.nc', engine='netcdf4')

# Calculate HII (Humidity Instability Index)
rainfall = ds.RAINFALL.values

# Calculate metrics over time
mean_rainfall = np.nanmean(rainfall, axis=0)
max_rainfall = np.nanmax(rainfall, axis=0)
std_rainfall = np.nanstd(rainfall, axis=0)

# HII = (Max rainfall * 0.5) + (Mean rainfall * 0.3) + (Std * 0.2)
hii = (max_rainfall * 0.5) + (mean_rainfall * 0.3) + (std_rainfall * 0.2)

print(f'Grid shape: {hii.shape}')
print(f'HII range: {hii.min():.1f} to {hii.max():.1f}')

# Get coordinates
lons = ds.LONGITUDE.values
lats = ds.LATITUDE.values

print(f'Longitude range: {lons.min():.2f} to {lons.max():.2f}')
print(f'Latitude range: {lats.min():.2f} to {lats.max():.2f}')

# Create custom colormap for heat map
colors = ['#00008B', '#0000CD', '#00BFFF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000', '#8B0000']
cmap = LinearSegmentedColormap.from_list('heatmap', colors, N=100)

# Create heat map
fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Plot heat map
im = ax.imshow(hii, extent=[lons.min(), lons.max(), lats.min(), lats.max()], 
               origin='lower', cmap=cmap, alpha=0.85, aspect='auto')

# Add colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.7)
cbar.set_label('HII Value (Higher = Higher Cloudburst Risk)', fontsize=12, fontweight='bold')

# Add district markers
districts = {
    'Uttarkashi': (78.4456, 30.7295),
    'Chamoli': (79.3301, 30.4183),
    'Rudraprayag': (78.9775, 30.2834),
    'Tehri': (78.4800, 30.3800),
    'Dehradun': (78.0322, 30.3165),
    'Pauri': (78.7700, 30.1500),
    'Almora': (79.6562, 29.5970),
    'Nainital': (79.4460, 29.3800),
    'Pithoragarh': (80.2090, 29.5830)
}

for name, (lon, lat) in districts.items():
    ax.plot(lon, lat, 'ko', markersize=8, markerfacecolor='white', markeredgewidth=2)
    ax.annotate(name, (lon, lat), xytext=(5, 5), textcoords='offset points', 
                fontsize=9, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

# Add labels and title
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.set_title('HII Heat Map - Uttarakhand (2024 IMD Data)\nHigher HII = Higher Cloudburst Risk', 
             fontsize=14, fontweight='bold')

# Add grid
ax.grid(True, alpha=0.3, linestyle='--')

# Save
plt.tight_layout()
plt.savefig('data/imd/uttarakhand_hii_heatmap.png', dpi=150, bbox_inches='tight')
print('\n✅ Static heat map saved to: data/imd/uttarakhand_hii_heatmap.png')

plt.show()
