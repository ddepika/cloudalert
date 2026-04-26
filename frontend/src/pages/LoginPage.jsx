// frontend/src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, { email, password });
      
      if (response.data.success) {
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userName', response.data.name);
        login(email, response.data.name);
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 450, margin: '0 auto' }}>
      <div style={{ padding: 32, backgroundColor: 'white', borderRadius: 16, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <h2 style={{ color: '#012060', textAlign: 'center', marginBottom: 8 }}>Welcome Back</h2>
        <p style={{ color: '#666', textAlign: 'center', marginBottom: 24 }}>Sign in to access your dashboard</p>

        {error && (
          <div style={{ backgroundColor: '#ffebee', color: '#c62828', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16 }}
            />
          </div>
          
          <div style={{ marginBottom: 24 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #ccc', fontSize: 16 }}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: 12, backgroundColor: '#012060', color: 'white', border: 'none', borderRadius: 8, fontSize: 16, fontWeight: 'bold', cursor: 'pointer' }}
          >
            {loading ? 'Signing in...' : 'Login'}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: 24, color: '#666' }}>
          Don't have an account? <Link to="/signup" style={{ color: '#012060', textDecoration: 'none' }}>Sign Up</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;