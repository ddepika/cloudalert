// frontend/src/pages/PredictionPage.jsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './PredictionPage.css';

const API_BASE = 'http://localhost:8000';

const PredictionPage = () => {
  const [districts, setDistricts] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('Uttarakhand');
  const [selectedDistrict, setSelectedDistrict] = useState('uttarkashi');
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
      const response = await axios.get(`${API_BASE}/api/weather/districts`);
      setDistricts(response.data.districts);
    } catch (err) {
      console.error('Failed to fetch districts:', err);
    }
  };

  const fetchStates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/weather/states`);
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
      const response = await axios.post(`${API_BASE}/api/prediction/predict`, {
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

  const getRiskClass = () => {
    if (!prediction) return 'low';
    if (prediction.risk_level === 'HIGH') return 'high';
    if (prediction.risk_level === 'MEDIUM') return 'medium';
    return 'low';
  };

  const getRiskColor = () => {
    if (!prediction) return '#4caf50';
    if (prediction.risk_level === 'HIGH') return '#d32f2f';
    if (prediction.risk_level === 'MEDIUM') return '#ff9800';
    return '#4caf50';
  };

  const filteredDistricts = getFilteredDistricts();

  return (
    <div className="prediction-wrapper">
      <div className="prediction-container">
        
        {/* Header */}
        <div className="prediction-header">
          <h1>Cloudburst Prediction</h1>
          <p>Enter weather parameters to assess cloudburst risk</p>
        </div>

        {/* Two Column Layout - Side by Side */}
        <div className="prediction-row">
          
          {/* Left Column - Form */}
          <div className="prediction-form-col">
            <div className="form-card">
              <h2 className="form-title">Input Parameters</h2>
              
              <div className="form-group">
                <label className="form-label">Select State</label>
                <select 
                  className="form-select"
                  value={selectedState}
                  onChange={handleStateChange}
                >
                  {states.map(state => (
                    <option key={state.name} value={state.name}>{state.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Select District</label>
                <select 
                  className="form-select"
                  value={selectedDistrict}
                  onChange={handleDistrictChange}
                >
                  {filteredDistricts.map(district => (
                    <option key={district.value} value={district.value}>{district.name}</option>
                  ))}
                </select>
              </div>

              {/* Two column layout for inputs */}
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Temperature (°C)</label>
                  <input
                    type="number"
                    name="temperature"
                    className="form-input"
                    value={formData.temperature}
                    onChange={handleChange}
                    step="0.1"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Humidity (%)</label>
                  <input
                    type="number"
                    name="humidity"
                    className="form-input"
                    value={formData.humidity}
                    onChange={handleChange}
                    step="1"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Pressure (hPa)</label>
                  <input
                    type="number"
                    name="pressure"
                    className="form-input"
                    value={formData.pressure}
                    onChange={handleChange}
                    step="1"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Wind Speed (m/s)</label>
                  <input
                    type="number"
                    name="wind_speed"
                    className="form-input"
                    value={formData.wind_speed}
                    onChange={handleChange}
                    step="0.1"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Cloud Cover (%)</label>
                <input
                  type="number"
                  name="cloud_cover"
                  className="form-input"
                  value={formData.cloud_cover}
                  onChange={handleChange}
                  step="1"
                />
              </div>

              <button 
                className="predict-button"
                onClick={handlePredict}
                disabled={loading || !selectedDistrict}
              >
                {loading ? 'Predicting...' : 'Predict Cloudburst Risk'}
              </button>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="prediction-result-col">
            <div className="result-card">
              <h2 className="result-title">Prediction Results</h2>
              
              {prediction ? (
                <div>
                  {/* Risk Alert */}
                  <div className={`risk-alert risk-alert-${getRiskClass()}`}>
                    <div className="risk-level" style={{ color: getRiskColor() }}>
                      Risk Level: {prediction.risk_level}
                    </div>
                    <div className="risk-probability" style={{ color: getRiskColor() }}>
                      {prediction.cloudburst_probability}%
                    </div>
                    <div className="risk-message">
                      {prediction.message}
                    </div>
                    <div className="risk-message" style={{ marginTop: '8px' }}>
                      Warning valid for: {prediction.warning_hours} hours
                    </div>
                  </div>

                  {/* Risk Trend Chart - Fixed overlapping */}
                  <div className="chart-container">
                    <div className="chart-title">Risk Trend (Next 6 Hours)</div>
                    <div className="chart-wrapper">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart 
                          data={chartData}
                          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis 
                            dataKey="hour" 
                            label={{ value: 'Hours from now', position: 'bottom', offset: 0 }}
                            tick={{ fontSize: 12 }}
                            interval={1}
                          />
                          <YAxis 
                            label={{ value: 'Risk (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                            tick={{ fontSize: 12 }}
                            domain={[0, 100]}
                          />
                          <Tooltip />
                          <Legend verticalAlign="top" height={36} />
                          <Line 
                            type="monotone" 
                            dataKey="risk" 
                            stroke="#ff0000" 
                            strokeWidth={2} 
                            dot={{ r: 4 }} 
                            name="Cloudburst Risk"
                            activeDot={{ r: 6 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="result-placeholder">
                  <p>Select a district, enter weather parameters,</p>
                  <p>and click predict to see results</p>
                </div>
              )}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default PredictionPage;