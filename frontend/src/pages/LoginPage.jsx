import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showResend, setShowResend] = useState(false);
  const [pendingEmail, setPendingEmail] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);

    if (params.get('verified') === 'true') {
      setSuccessMessage('Email verified successfully. You can now login.');
      // Clear URL params
      navigate('/login', { replace: true });
    }

    if (params.get('error') === 'invalid_token') {
      setError('Invalid verification link. Please request a new one.');
      navigate('/login', { replace: true });
    }

    if (params.get('error') === 'token_expired') {
      setError('Verification link expired. Please request a new one.');
      navigate('/login', { replace: true });
    }
  }, [location, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');
    setShowResend(false);

    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, { email, password });

      if (response.data.success && response.data.verified) {
        login(email, response.data.name);
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userName', response.data.name);
        navigate('/');
      } else if (!response.data.verified) {
        setError(response.data.message);
        setShowResend(true);
        setPendingEmail(email);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    }
    setLoading(false);
  };

  const handleResendVerification = async () => {
    const emailToResend = pendingEmail || email;
    if (!emailToResend) {
      setError('Please enter your email address first');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/auth/resend-verification?email=${emailToResend}`);
      setSuccessMessage('Verification email resent. Please check your inbox.');
      setShowResend(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resend verification email');
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

        {successMessage && (
          <div style={{ backgroundColor: '#e8f5e9', color: '#2e7d32', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            {successMessage}
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

        {showResend && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <button
              onClick={handleResendVerification}
              style={{ color: '#012060', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
            >
              Resend Verification Email
            </button>
          </div>
        )}

        <p style={{ textAlign: 'center', marginTop: 24, color: '#666' }}>
          Don't have an account? <Link to="/signup" style={{ color: '#012060', textDecoration: 'none' }}>Sign Up</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;