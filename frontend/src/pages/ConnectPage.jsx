// frontend/src/pages/ConnectPage.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const ConnectPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [district, setDistrict] = useState('uttarkashi');
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [weatherData, setWeatherData] = useState(null);

  useEffect(() => {
    fetchDistricts();
    fetchWeather();
  }, []);

  const fetchDistricts = async () => {
    try {
      const response = await axios.get(API_BASE + '/api/weather/districts');
      setDistricts(response.data.districts || []);
    } catch (err) {
      console.error('Failed to fetch districts:', err);
    }
  };

  const fetchWeather = async () => {
    try {
      const response = await axios.get(API_BASE + '/api/weather/live/uttarkashi');
      setWeatherData(response.data);
    } catch (err) {
      console.error('Failed to fetch weather:', err);
    }
  };

  const getRisk = () => {
    if (!weatherData) return 'Low';
    if (weatherData.humidity > 90 && weatherData.pressure < 1005) return 'High';
    if (weatherData.humidity > 70 && weatherData.pressure < 1010) return 'Medium';
    return 'Low';
  };

  const getRiskProbability = () => {
    if (!weatherData) return 0;
    if (weatherData.humidity > 90 && weatherData.pressure < 1005) return 85;
    if (weatherData.humidity > 70 && weatherData.pressure < 1010) return 55;
    return 20;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      // Get current weather for selected district
      const weatherResponse = await axios.get(API_BASE + '/api/weather/live/' + district);
      const currentWeather = weatherResponse.data;
      
      // Calculate risk
      let riskLevel = 'Low';
      let probability = 20;
      if (currentWeather.humidity > 90 && currentWeather.pressure < 1005) {
        riskLevel = 'High';
        probability = 85;
      } else if (currentWeather.humidity > 70 && currentWeather.pressure < 1010) {
        riskLevel = 'Medium';
        probability = 55;
      }

      // Send alert email
      await axios.post(API_BASE + '/api/auth/send-alert', {
        email: email,
        name: name,
        district: district,
        risk_level: riskLevel,
        probability: probability
      });

      setMessage(`Weather report sent successfully to ${email}!`);
      setName('');
      setEmail('');
    } catch (err) {
      setError('Failed to send report. Please try again.');
      console.error('Error:', err);
    }
    setLoading(false);
  };

  const filteredDistricts = districts.filter(d => d.state === 'Uttarakhand');

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <div style={{ padding: 32, backgroundColor: 'white', borderRadius: 16, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>📧</div>
          <h2 style={{ color: '#012060', marginBottom: 8 }}>Get Weather Report</h2>
          <p style={{ color: '#666' }}>Receive cloudburst alerts and weather updates via email</p>
        </div>

        {message && (
          <div style={{ backgroundColor: '#e8f5e9', color: '#2e7d32', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            {message}
          </div>
        )}
        
        {error && (
          <div style={{ backgroundColor: '#ffebee', color: '#c62828', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Your Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Enter your full name"
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16 }}
            />
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16 }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>District to Monitor</label>
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16, backgroundColor: 'white' }}
            >
              {filteredDistricts.map(d => (
                <option key={d.value} value={d.value}>{d.name}</option>
              ))}
            </select>
          </div>

          {/* Current Weather Preview */}
          {weatherData && (
            <div style={{ marginBottom: 20, padding: 16, backgroundColor: '#E1EBF7', borderRadius: 12 }}>
              <h4 style={{ marginBottom: 12, color: '#012060' }}>Current Conditions for {district}</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
                <div><strong>Temperature:</strong> {weatherData.temperature}°C</div>
                <div><strong>Humidity:</strong> {weatherData.humidity}%</div>
                <div><strong>Pressure:</strong> {weatherData.pressure} hPa</div>
                <div><strong>Wind Speed:</strong> {weatherData.wind_speed} m/s</div>
              </div>
              <div style={{ marginTop: 12, padding: 8, backgroundColor: 'white', borderRadius: 8, textAlign: 'center' }}>
                <strong style={{ color: '#012060' }}>Current Risk: {getRisk()} ({getRiskProbability()}%)</strong>
              </div>
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: 14, backgroundColor: '#012060', color: 'white', border: 'none', borderRadius: 8, fontSize: 16, fontWeight: 'bold', cursor: 'pointer' }}
          >
            {loading ? 'Sending Report...' : 'Send Weather Report'}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: '#999' }}>
          You will receive cloudburst alerts and weather updates for your selected district.
        </p>
      </div>
    </div>
  );
};

export default ConnectPage;