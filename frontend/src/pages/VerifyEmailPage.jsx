import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const VerifyEmailPage = () => {
  const { user, verifyUser, logout } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkVerification();
  }, []);

  const checkVerification = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/api/auth/check-verification?email=${user.email}`);
      if (response.data.verified) {
        verifyUser();
        navigate('/');
      }
    } catch (error) {
      console.error('Check failed:', error);
    } finally {
      setChecking(false);
    }
  };

// frontend/src/pages/VerifyEmailPage.jsx - Update the handleResendVerification function

const handleResendVerification = async () => {
  setLoading(true);
  try {
    const response = await axios.post(`${API_BASE}/api/auth/resend-verification?email=${user.email}`);
    setMessage(response.data.message);
  } catch (error) {
    setMessage(error.response?.data?.detail || 'Failed to resend verification email. Please try again.');
  }
  setLoading(false);
};

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (checking) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ width: 40, height: 40, border: '3px solid #f3f3f3', borderTop: '3px solid #012060', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 500, margin: '0 auto', padding: 20 }}>
      <div style={{ backgroundColor: 'white', borderRadius: 16, padding: 32, boxShadow: '0 2px 10px rgba(0,0,0,0.1)', textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 16 }}> </div>
        <h2 style={{ color: '#012060', marginBottom: 16 }}>Verify Your Email</h2>
        <p style={{ color: '#666', marginBottom: 24 }}>
          We sent a verification link to <strong>{user?.email}</strong>. Please check your email and click the verification link to activate your account.
        </p>
        
        {message && (
          <div style={{ backgroundColor: '#e8f5e9', color: '#2e7d32', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            {message}
          </div>
        )}
        
        <button
          onClick={handleResendVerification}
          disabled={loading}
          style={{ width: '100%', padding: 12, backgroundColor: '#012060', color: 'white', border: 'none', borderRadius: 8, fontSize: 16, cursor: 'pointer', marginBottom: 12 }}
        >
          {loading ? 'Sending...' : 'Resend Verification Email'}
        </button>
        
        <button
          onClick={handleLogout}
          style={{ width: '100%', padding: 12, backgroundColor: '#f5f5f5', color: '#666', border: '1px solid #ddd', borderRadius: 8, fontSize: 16, cursor: 'pointer' }}
        >
          Go Back to Login
        </button>
      </div>
    </div>
  );
};

export default VerifyEmailPage;