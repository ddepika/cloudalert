import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const ConnectPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [filteredDistricts, setFilteredDistricts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [loggedInUser, setLoggedInUser] = useState(null);

  useEffect(() => {
    const userEmail = localStorage.getItem('userEmail');
    const userName = localStorage.getItem('userName');
    
    if (userEmail) {
      setLoggedInUser({ email: userEmail, name: userName });
      // Do not auto-fill email - let user enter any email
    }
    
    fetchStates();
    fetchDistricts();
    fetchWeather();
  }, []);

  const fetchStates = async () => {
    try {
      const response = await axios.get(API_BASE + '/api/weather/states');
      setStates(response.data.states || []);
      if (response.data.states && response.data.states.length > 0) {
        setSelectedState(response.data.states[0].name);
      }
    } catch (err) {
      console.error('Failed to fetch states:', err);
    }
  };

  const fetchDistricts = async () => {
    try {
      const response = await axios.get(API_BASE + '/api/weather/districts');
      setDistricts(response.data.districts || []);
    } catch (err) {
      console.error('Failed to fetch districts:', err);
    }
  };

  const fetchWeather = async (district = 'uttarkashi') => {
    try {
      const response = await axios.get(API_BASE + '/api/weather/live/' + district);
      setWeatherData(response.data);
    } catch (err) {
      console.error('Failed to fetch weather:', err);
    }
  };

  useEffect(() => {
    if (selectedState && districts.length > 0) {
      const filtered = districts.filter(d => d.state === selectedState);
      setFilteredDistricts(filtered);
      if (filtered.length > 0) {
        setSelectedDistrict(filtered[0].value);
        fetchWeather(filtered[0].value);
      }
    }
  }, [selectedState, districts]);

  const handleDistrictChange = (e) => {
    const district = e.target.value;
    setSelectedDistrict(district);
    fetchWeather(district);
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
      const response = await axios.post(API_BASE + '/api/auth/send-alert', {
        email: email,
        name: name,
        district: selectedDistrict,
        risk_level: getRisk(),
        probability: getRiskProbability()
      });
      
      setMessage(`Weather report sent successfully to ${email}`);
      // Clear form after sending
      setName('');
      setEmail('');
    } catch (err) {
      setError('Failed to send report. Please try again.');
      console.error('Error:', err);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <div style={{ padding: 32, backgroundColor: 'white', borderRadius: 16, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h2 style={{ color: '#012060', marginBottom: 8 }}>Get Weather Report</h2>
          <p style={{ color: '#666' }}>Receive cloudburst alerts and weather updates via email</p>
        </div>

        {loggedInUser && (
          <div style={{ backgroundColor: '#E1EBF7', padding: 12, borderRadius: 8, marginBottom: 16, textAlign: 'center' }}>
            Logged in as: <strong>{loggedInUser.email}</strong> - You can send reports to any email address
          </div>
        )}

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
            <p style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
              Enter any email address to receive the weather report
            </p>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Select State</label>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16, backgroundColor: 'white' }}
            >
              {states.map(state => (
                <option key={state.name} value={state.name}>{state.name}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Select District</label>
            <select
              value={selectedDistrict}
              onChange={handleDistrictChange}
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16, backgroundColor: 'white' }}
            >
              {filteredDistricts.map(district => (
                <option key={district.value} value={district.value}>{district.name}</option>
              ))}
            </select>
          </div>

          {weatherData && (
            <div style={{ marginBottom: 20, padding: 16, backgroundColor: '#E1EBF7', borderRadius: 12 }}>
              <h4 style={{ marginBottom: 12, color: '#012060' }}>Current Conditions for {selectedDistrict}</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
                <div><strong>Temperature:</strong> {weatherData.temperature}°C</div>
                <div><strong>Humidity:</strong> {weatherData.humidity}%</div>
                <div><strong>Pressure:</strong> {weatherData.pressure} hPa</div>
                <div><strong>Wind Speed:</strong> {weatherData.wind_speed} m/s</div>
                <div><strong>Cloud Cover:</strong> {weatherData.cloud_cover}%</div>
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
          You can send reports to any email address, not just your registered email.
        </p>
      </div>
    </div>
  );
};

export default ConnectPage;