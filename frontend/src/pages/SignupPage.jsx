import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const SignupPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/auth/register`, { 
        name, 
        email, 
        password 
      });
      
      if (response.data.success) {
        setMessage(response.data.message);
        setTimeout(() => navigate('/login'), 4000);
      } else {
        setMessage(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 450, margin: '0 auto' }}>
      <div style={{ padding: 32, backgroundColor: 'white', borderRadius: 16, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <h2 style={{ color: '#012060', textAlign: 'center', marginBottom: 8 }}>Create Account</h2>
        <p style={{ color: '#666', textAlign: 'center', marginBottom: 24 }}>Join CloudAlert for personalized alerts</p>

        {message && (
          <div style={{ backgroundColor: '#e8f5e9', color: '#012060', padding: 12, borderRadius: 8, marginBottom: 16 }}>
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
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold', color: '#333' }}>Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
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
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: 24, color: '#666' }}>
          Already have an account? <Link to="/login" style={{ color: '#012060', textDecoration: 'none' }}>Login</Link>
        </p>
      </div>
    </div>
  );
};

export default SignupPage;