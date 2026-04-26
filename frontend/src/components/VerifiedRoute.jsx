import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const VerifiedRoute = ({ children }) => {
  const { user, isVerified, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ width: 40, height: 40, border: '3px solid #f3f3f3', borderTop: '3px solid #012060', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!isVerified) {
    return <Navigate to="/verify-email" replace />;
  }

  return children;
};

export default VerifiedRoute;