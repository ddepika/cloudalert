import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const VerifiedRoute = ({ children }) => {
  const { user, isVerified, loading } = useAuth();

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 50 }}>Loading...</div>;
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