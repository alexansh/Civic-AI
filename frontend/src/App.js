/**
 * Main App Component
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import CitizenDashboard from './pages/citizen/Dashboard';
import VendorDashboard from './pages/vendor/Dashboard';
import GovernmentDashboard from './pages/government/Dashboard';
import AdminDashboard from './pages/admin/Dashboard';
import CreateComplaint from './pages/citizen/CreateComplaint';
import ComplaintDetails from './pages/citizen/ComplaintDetails';
import NotFound from './pages/NotFound';
import RoleSelection from './pages/RoleSelection';

// Components
import Header from './components/Header';

// Auth utilities
import { isAuthenticated, getRole, logout } from './utils/auth';
import { AuthProvider } from './context/AuthContext';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && getRole() !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <div className="App">
            {/* Header - shown on all pages except login/register/role selection */}
            {!(
              window.location.pathname === '/login' ||
              window.location.pathname === '/register' ||
              window.location.pathname === '/'
            ) && <Header />}

            <main
              style={{
                marginTop: !(
                  window.location.pathname === '/login' ||
                  window.location.pathname === '/register' ||
                  window.location.pathname === '/'
                )
                  ? 64
                  : 0, /* Header height */
                minHeight: '100vh',
                paddingTop: !(
                  window.location.pathname === '/login' ||
                  window.location.pathname === '/register' ||
                  window.location.pathname === '/'
                )
                  ? 20
                  : 0,
              }}
            >
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Citizen Routes */}
                <Route
                  path="/citizen/dashboard"
                  element={
                    <ProtectedRoute requiredRole="citizen">
                      <CitizenDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/citizen/create-complaint"
                  element={
                    <ProtectedRoute requiredRole="citizen">
                      <CreateComplaint />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/citizen/complaint/:id"
                  element={
                    <ProtectedRoute>
                      <ComplaintDetails />
                    </ProtectedRoute>
                  }
                />

                {/* Vendor Routes */}
                <Route
                  path="/vendor/dashboard"
                  element={
                    <ProtectedRoute requiredRole="vendor">
                      <VendorDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Government Routes */}
                <Route
                  path="/government/dashboard"
                  element={
                    <ProtectedRoute requiredRole="government">
                      <GovernmentDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Admin Routes */}
                <Route
                  path="/admin/dashboard"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <AdminDashboard />
                    </ProtectedRoute>
                  }
                />

                /* 