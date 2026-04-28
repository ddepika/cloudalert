import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { AuthProvider, useAuth } from './context/AuthContext';
import HomePage from './pages/HomePage';
import PredictionPage from './pages/PredictionPage';
import ConnectPage from './pages/ConnectPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import ProtectedRoute from './components/ProtectedRoute';
import VerifiedRoute from './components/VerifiedRoute';
import './App.css';
import logo from './assets/logo.png';

const NavBar = () => {
  const { user, logout } = useAuth();
  const location = window.location.pathname;

  const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Prediction', path: '/prediction' },
    { name: 'Connect', path: '/connect' },
  ];

  return (
    <Box className="navbar">
      <div className="nav-container">
        <Link to="/" className="logo-link">
          <div className="logo">
            <img src={logo} alt="CloudAlert Logo" className="logo-image" style={{ width: '50px' }} />
            <span className="logo-text">CloudAlert</span>
          </div>
        </Link>
        <div className="nav-links">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${location === item.path ? 'active' : ''}`}
            >
              {item.name}
            </Link>
          ))}
          {user ? (
            <>
              <span className="nav-user">
                <AccountCircleIcon className="nav-user-icon" />
                {user.name}
              </span>
              <button onClick={logout} className="nav-logout">Logout</button>
            </>
          ) : (
            <Link to="/login" className="nav-link">Login</Link>
          )}
        </div>
      </div>
    </Box>
  );
};

function AppRoutes() {
  const location = useLocation();
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    // Check for token in URL (from email verification)
    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    const name = params.get('name');
    const email = params.get('email');
    
    if (token && name && email) {
      // Auto-login the user
      localStorage.setItem('userEmail', email);
      localStorage.setItem('userName', name);
      localStorage.setItem('authToken', token);
      login(email, name);
      
      // Clean URL and redirect to home
      navigate('/', { replace: true });
    }
  }, [location, navigate, login]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <HomePage />
        </ProtectedRoute>
      } />
      
      <Route path="/prediction" element={
        <VerifiedRoute>
          <PredictionPage />
        </VerifiedRoute>
      } />
      
      <Route path="/connect" element={
        <VerifiedRoute>
          <ConnectPage />
        </VerifiedRoute>
      } />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Box sx={{ flexGrow: 1 }}>
          <NavBar />
          <Container maxWidth="xl" className="main-container">
            <AppRoutes />
          </Container>
        </Box>
      </AuthProvider>
    </Router>
  );
}

export default App;