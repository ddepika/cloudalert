import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, TextField, Button, Box, Alert, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const PredictionPage = () => {
  const [districts, setDistricts] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [formData, setFormData] = useState({
    temperature: 25,
    humidity: 65,
    pressure: 1013,
    wind_speed: 2.5,
    cloud_cover: 40
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchDistricts();
    fetchStates();
  }, []);

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

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
  };

  const handleStateChange = (event) => {
    setSelectedState(event.target.value);
    setSelectedDistrict('');
  };

  const handleDistrictChange = (event) => {
    setSelectedDistrict(event.target.value);
  };

  const handlePredict = async () => {
    if (!selectedDistrict) {
      alert('Please select a district first');
      return;
    }
    
    setLoading(true);
    try {
      const url = 'http://localhost:8000/api/prediction/predict';
      const response = await axios.post(url, {
        district: selectedDistrict,
        temperature: formData.temperature,
        humidity: formData.humidity,
        pressure: formData.pressure,
        wind_speed: formData.wind_speed,
        wind_direction: 180,
        cloud_cover: formData.cloud_cover,
        rainfall_1h: 0
      });
      setPrediction(response.data);
      
      const data = [];
      for (let i = -6; i <= 6; i++) {
        let risk = response.data.cloudburst_probability + (i * 2);
        risk = Math.min(100, Math.max(0, risk));
        data.push({ hour: i, risk: risk });
      }
      setChartData(data);
    } catch (error) {
      console.error('Prediction failed:', error);
    }
    setLoading(false);
  };

  const getFilteredDistricts = () => {
    if (!selectedState) return districts;
    return districts.filter(d => d.state === selectedState);
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={5}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Cloudburst Prediction</Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select State</InputLabel>
            <Select value={selectedState} onChange={handleStateChange} label="Select State">
              <MenuItem value="">All States</MenuItem>
              {states.map(state => (
                <MenuItem key={state.name} value={state.name}>{state.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select District</InputLabel>
            <Select value={selectedDistrict} onChange={handleDistrictChange} label="Select District">
              <MenuItem value="">Select a district</MenuItem>
              {getFilteredDistricts().map(district => (
                <MenuItem key={district.value} value={district.value}>{district.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField fullWidth label="Temperature (degC)" name="temperature" type="number" value={formData.temperature} onChange={handleChange} sx={{ mb: 2 }} />
          <TextField fullWidth label="Humidity (%)" name="humidity" type="number" value={formData.humidity} onChange={handleChange} sx={{ mb: 2 }} />
          <TextField fullWidth label="Pressure (hPa)" name="pressure" type="number" value={formData.pressure} onChange={handleChange} sx={{ mb: 2 }} />
          <TextField fullWidth label="Wind Speed (m/s)" name="wind_speed" type="number" value={formData.wind_speed} onChange={handleChange} sx={{ mb: 2 }} />
          <TextField fullWidth label="Cloud Cover (%)" name="cloud_cover" type="number" value={formData.cloud_cover} onChange={handleChange} sx={{ mb: 2 }} />
          
          <Button fullWidth variant="contained" onClick={handlePredict} disabled={loading || !selectedDistrict} sx={{ mt: 2 }}>
            {loading ? 'Predicting...' : 'Predict Cloudburst Risk'}
          </Button>
        </Paper>
      </Grid>

      <Grid item xs={12} md={7}>
        <Paper elevation={3} sx={{ p: 3, height: '100%', minHeight: '500px' }}>
          <Typography variant="h5" gutterBottom>Prediction Results</Typography>
          {prediction ? (
            <Box>
              <Alert 
                severity={prediction.risk_level === 'HIGH' ? 'error' : prediction.risk_level === 'MEDIUM' ? 'warning' : 'success'} 
                sx={{ mb: 3 }}
              >
                <Typography variant="h6">Risk Level: {prediction.risk_level}</Typography>
                <Typography>Probability: {prediction.cloudburst_probability}%</Typography>
                <Typography>{prediction.message}</Typography>
                <Typography variant="caption">Warning valid for: {prediction.warning_hours} hours</Typography>
              </Alert>
              <Typography variant="h6" gutterBottom>Risk Trend (Next 6 hours)</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" label={{ value: 'Hours from now', position: 'bottom' }} />
                  <YAxis label={{ value: 'Risk (%)', angle: -90, position: 'insideLeft' }} domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="risk" stroke="#ff0000" strokeWidth={2} dot={{ r: 3 }} name="Cloudburst Risk" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Typography color="textSecondary">Select a district, enter weather parameters, and click predict to see results</Typography>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default PredictionPage;
