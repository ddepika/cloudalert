import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress, Alert, FormControl, InputLabel, Select, MenuItem, Card, CardContent } from '@mui/material';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import { WiThermometer, WiHumidity, WiBarometer, WiStrongWind } from 'react-icons/wi';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const HomePage = () => {
  const [districts, setDistricts] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDistricts();
    fetchStates();
  }, []);

  useEffect(() => {
    if (selectedDistrict) {
      fetchWeatherData();
      const interval = setInterval(fetchWeatherData, 300000);
      return () => clearInterval(interval);
    }
  }, [selectedDistrict]);

  const fetchDistricts = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/weather/districts');
      setDistricts(response.data.districts);
    } catch (err) {
      console.error('Failed to fetch districts:', err);
    }
  };

  const fetchStates = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/weather/states');
      setStates(response.data.states);
    } catch (err) {
      console.error('Failed to fetch states:', err);
    }
  };

  const fetchWeatherData = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = 'http://localhost:8000/api/weather/live/' + selectedDistrict;
      const response = await axios.get(url);
      setWeatherData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch weather data');
      setLoading(false);
    }
  };

  const getDistrictCoords = () => {
    const district = districts.find(d => d.value === selectedDistrict);
    return district ? [district.lat, district.lng] : [30.3165, 78.0322];
  };

  const getFilteredDistricts = () => {
    if (!selectedState) return districts;
    return districts.filter(d => d.state === selectedState);
  };

  const FeatureCard = ({ icon, title, value, unit }) => (
    <Card sx={{ textAlign: 'center', height: '100%' }}>
      <CardContent>
        <Box fontSize={40}>{icon}</Box>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="h4" color="primary">{value !== undefined ? value : '--'}</Typography>
        <Typography variant="body2" color="textSecondary">{unit}</Typography>
      </CardContent>
    </Card>
  );

  if (!selectedDistrict) {
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Select State</InputLabel>
            <Select value={selectedState} onChange={(e) => setSelectedState(e.target.value)} label="Select State">
              <MenuItem value="">All States</MenuItem>
              {states.map(state => (
                <MenuItem key={state.name} value={state.name}>{state.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Select District</InputLabel>
            <Select value={selectedDistrict} onChange={(e) => setSelectedDistrict(e.target.value)} label="Select District">
              <MenuItem value="">Select a district</MenuItem>
              {getFilteredDistricts().map(district => (
                <MenuItem key={district.value} value={district.value}>{district.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6">Please select a state and district to view weather data</Typography>
          </Paper>
        </Grid>
      </Grid>
    );
  }

  if (loading && !weatherData) {
    return <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
      <CircularProgress />
    </Box>;
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Select State</InputLabel>
          <Select value={selectedState} onChange={(e) => setSelectedState(e.target.value)} label="Select State">
            <MenuItem value="">All States</MenuItem>
            {states.map(state => (
              <MenuItem key={state.name} value={state.name}>{state.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Select District</InputLabel>
          <Select value={selectedDistrict} onChange={(e) => setSelectedDistrict(e.target.value)} label="Select District">
            <MenuItem value="">Select a district</MenuItem>
            {getFilteredDistricts().map(district => (
              <MenuItem key={district.value} value={district.value}>{district.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Grid>
      )}

      {weatherData && (
        <>
          <Grid item xs={12}>
            <Typography variant="h5" align="center" gutterBottom>
              {weatherData.district?.charAt(0).toUpperCase() + weatherData.district?.slice(1)}, {weatherData.state}
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2, height: '500px' }}>
              <Typography variant="h6" gutterBottom>Live Weather Map</Typography>
              <MapContainer center={getDistrictCoords()} zoom={10} style={{ height: '440px', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <Marker position={getDistrictCoords()}>
                  <Popup>
                    <strong>{weatherData.district}</strong><br />
                    Temp: {weatherData.temperature}°C<br />
                    Humidity: {weatherData.humidity}%<br />
                    Wind: {weatherData.wind_speed} m/s
                  </Popup>
                </Marker>
                <Circle center={getDistrictCoords()} radius={15000} pathOptions={{ color: '#ff0000', fillOpacity: 0.2 }} />
              </MapContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FeatureCard icon={<WiThermometer size={40} />} title="Temperature" value={weatherData.temperature} unit="°C" />
              </Grid>
              <Grid item xs={6}>
                <FeatureCard icon={<WiHumidity size={40} />} title="Humidity" value={weatherData.humidity} unit="%" />
              </Grid>
              <Grid item xs={6}>
                <FeatureCard icon={<WiBarometer size={40} />} title="Pressure" value={weatherData.pressure} unit="hPa" />
              </Grid>
              <Grid item xs={6}>
                <FeatureCard icon={<WiStrongWind size={40} />} title="Wind Speed" value={weatherData.wind_speed} unit="m/s" />
              </Grid>
            </Grid>
          </Grid>
        </>
      )}
    </Grid>
  );
};

export default HomePage;
