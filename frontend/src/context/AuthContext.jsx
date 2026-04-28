import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();
const API_BASE = 'http://localhost:8000';

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const userEmail = localStorage.getItem('userEmail');
    const userName = localStorage.getItem('userName');
    const token = localStorage.getItem('authToken');
    
    if (userEmail && userName) {
      try {
        const response = await axios.get(`${API_BASE}/api/auth/check-verification?email=${userEmail}`);
        setIsVerified(response.data.verified);
        setUser({ email: userEmail, name: userName, verified: response.data.verified });
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    }
    setLoading(false);
  };

  const login = (email, name) => {
    localStorage.setItem('userEmail', email);
    localStorage.setItem('userName', name);
    setUser({ email, name, verified: false });
    setIsVerified(false);
    // Check verification status
    checkAuth();
  };

  const logout = () => {
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    localStorage.removeItem('authToken');
    setUser(null);
    setIsVerified(false);
  };

  const verifyUser = () => {
    setIsVerified(true);
    if (user) {
      setUser({ ...user, verified: true });
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, isVerified, login, logout, verifyUser }}>
      {children}
    </AuthContext.Provider>
  );
};