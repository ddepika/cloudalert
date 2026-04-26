// frontend/src/pages/HomePage.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const HomePage = () => {
  const [districts, setDistricts] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('Uttarakhand');
  const [selectedDistrict, setSelectedDistrict] = useState('uttarkashi');
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // District coordinates mapping
  const districtCoordsMap = {
    'uttarakhand': { uttarkashi: { lat: 30.7295, lng: 78.4456, name: 'Uttarkashi' },
                     chamoli: { lat: 30.4183, lng: 79.3301, name: 'Chamoli' },
                     rudraprayag: { lat: 30.2834, lng: 78.9775, name: 'Rudraprayag' },
                     bageshwar: { lat: 29.8497, lng: 79.7714, name: 'Bageshwar' },
                     pithoragarh: { lat: 29.5828, lng: 80.2188, name: 'Pithoragarh' } },
    'himachal pradesh': { mandi: { lat: 31.7085, lng: 76.9312, name: 'Mandi' },
                          shimla: { lat: 31.1048, lng: 77.1734, name: 'Shimla' },
                          chamba: { lat: 32.5555, lng: 76.1301, name: 'Chamba' },
                          kullu: { lat: 31.9581, lng: 77.1082, name: 'Kullu' },
                          kangra: { lat: 32.1103, lng: 76.2752, name: 'Kangra' } },
    'jammu & kashmir': { anantnag: { lat: 33.7345, lng: 75.1584, name: 'Anantnag' },
                         kulgam: { lat: 33.6444, lng: 75.0201, name: 'Kulgam' },
                         kishtwar: { lat: 33.3139, lng: 75.7670, name: 'Kishtwar' },
                         doda: { lat: 33.1441, lng: 75.5472, name: 'Doda' },
                         udhampur: { lat: 32.9256, lng: 75.1414, name: 'Udhampur' } }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedDistrict) {
      fetchWeather();
    }
  }, [selectedDistrict]);

  const loadData = async () => {
    setLoading(true);
    try {
      await axios.get(API_BASE + '/health');
      
      const [districtsRes, statesRes] = await Promise.all([
        axios.get(API_BASE + '/api/weather/districts'),
        axios.get(API_BASE + '/api/weather/states')
      ]);
      
      setDistricts(districtsRes.data.districts || []);
      setStates(statesRes.data.states || []);
      
      const weatherRes = await axios.get(API_BASE + '/api/weather/live/uttarkashi');
      setWeatherData(weatherRes.data);
      
      setError(null);
    } catch (err) {
      setError('Backend not running on port 8000');
    } finally {
      setLoading(false);
    }
  };

  const fetchWeather = async () => {
    try {
      const response = await axios.get(API_BASE + '/api/weather/live/' + selectedDistrict);
      setWeatherData(response.data);
    } catch (err) {
      console.error('Weather fetch failed:', err);
    }
  };

  const getRisk = () => {
    if (!weatherData) return 'Low';
    if (weatherData.humidity > 90 && weatherData.pressure < 1005) return 'High';
    if (weatherData.humidity > 70 && weatherData.pressure < 1010) return 'Medium';
    return 'Low';
  };

  const getRiskColor = () => {
    const risk = getRisk();
    if (risk === 'High') return '#d32f2f';
    if (risk === 'Medium') return '#ff9800';
    return '#4caf50';
  };

  const getDistrictCoords = () => {
    try {
      const stateKey = selectedState.toLowerCase();
      const districtKey = selectedDistrict.toLowerCase();
      if (districtCoordsMap[stateKey] && districtCoordsMap[stateKey][districtKey]) {
        const d = districtCoordsMap[stateKey][districtKey];
        return { lat: d.lat, lng: d.lng, name: d.name };
      }
    } catch (e) {
      console.error('Error getting coords:', e);
    }
    return { lat: 30.7295, lng: 78.4456, name: 'Uttarkashi' };
  };

  const filteredDistricts = districts.filter(d => d.state === selectedState);
  const coords = getDistrictCoords();
  const safeLat = coords.lat;
  const safeLng = coords.lng;
  const districtDisplayName = coords.name;

  // Google Maps static image alternative (requires API key for full features)
  // Using OpenStreetMap with better zoom and marker
  const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${safeLng - 0.15},${safeLat - 0.1},${safeLng + 0.15},${safeLat + 0.1}&layer=mapnik&marker=${safeLat},${safeLng}`;

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ width: 40, height: 40, border: '3px solid #f3f3f3', borderTop: '3px solid #012060', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <div style={{ backgroundColor: '#ffebee', color: '#c62828', padding: 16, borderRadius: 8 }}>
          <strong>Error:</strong> {error}
        </div>
        <p style={{ marginTop: 16 }}>Please start backend: cd backend && python run.py</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <h1 style={{ color: '#012060', fontWeight: 'bold', fontSize: 48, marginBottom: 8 }}>CloudAlert</h1>
        <p style={{ color: '#666', fontSize: 18 }}>Smarter Cloudburst Prediction for Safer Mountain Communities</p>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <label style={{ fontSize: 14, fontWeight: 'bold', color: '#012060', marginBottom: 8, display: 'block' }}>Select State</label>
          <select 
            value={selectedState}
            onChange={(e) => {
              setSelectedState(e.target.value);
              setSelectedDistrict('');
              setWeatherData(null);
            }}
            style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16, backgroundColor: 'white' }}
          >
            {states.map(state => (
              <option key={state.name} value={state.name}>{state.name}</option>
            ))}
          </select>
        </div>
        
        <div style={{ flex: 1 }}>
          <label style={{ fontSize: 14, fontWeight: 'bold', color: '#012060', marginBottom: 8, display: 'block' }}>Select District</label>
          <select 
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            disabled={filteredDistricts.length === 0}
            style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16, backgroundColor: 'white' }}
          >
            {filteredDistricts.map(district => (
              <option key={district.value} value={district.value}>{district.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Weather Data */}
      {weatherData && (
        <>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <div style={{ display: 'inline-block', padding: '8px 24px', backgroundColor: getRiskColor(), color: 'white', borderRadius: 50 }}>
              <strong>Risk: {getRisk()}</strong>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, marginBottom: 32 }}>
            {[
              { value: weatherData.temperature, unit: '°C', label: 'Temperature' },
              { value: weatherData.humidity, unit: '%', label: 'Humidity' },
              { value: weatherData.pressure, unit: 'hPa', label: 'Pressure' },
              { value: weatherData.wind_speed, unit: 'm/s', label: 'Wind Speed' },
              { value: weatherData.cloud_cover, unit: '%', label: 'Cloud Cover' }
            ].map((item, idx) => (
              <div key={idx} style={{ padding: 16, textAlign: 'center', backgroundColor: '#E1EBF7', borderRadius: 16 }}>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#012060' }}>{item.value}{item.unit}</div>
                <div style={{ fontSize: 14, color: '#666' }}>{item.label}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Live Map */}
      <div style={{ padding: 16, backgroundColor: 'white', borderRadius: 16, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <h3 style={{ marginBottom: 16, color: '#012060' }}>Live Map - {districtDisplayName}</h3>
        
        <div style={{ height: 400, backgroundColor: '#f5f5f5', borderRadius: 12, overflow: 'hidden' }}>
          <iframe
            title="location-map"
            width="100%"
            height="100%"
            style={{ border: 'none' }}
            src={mapUrl}
          />
        </div>
        
        <div style={{ marginTop: 12, fontSize: 13, color: '#666', textAlign: 'center' }}>
          <div><strong>{districtDisplayName}</strong>, {selectedState}</div>
          <div style={{ marginTop: 4 }}> Coordinates: {safeLat.toFixed(4)}°N, {safeLng.toFixed(4)}°E</div>
          <div style={{ marginTop: 8, fontSize: 11, color: '#999' }}>
            Map shows the district area (zoomed to 10km radius)
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;