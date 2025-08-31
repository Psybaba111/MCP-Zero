/**
 * EV Platform Operations Dashboard
 * React dashboard for ride monitoring, listing approvals, and booking management
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';

import { AuthProvider } from './contexts/AuthContext';
import { ApiProvider } from './contexts/ApiContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import RideMonitoring from './pages/RideMonitoring';
import ListingApprovals from './pages/ListingApprovals';
import BookingMonitor from './pages/BookingMonitor';
import AuditLogs from './pages/AuditLogs';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  palette: {
    primary: {
      main: '#4CAF50',
    },
    secondary: {
      main: '#2196F3',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <ApiProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/rides" element={
                <ProtectedRoute>
                  <Layout>
                    <RideMonitoring />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/approvals" element={
                <ProtectedRoute>
                  <Layout>
                    <ListingApprovals />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/bookings" element={
                <ProtectedRoute>
                  <Layout>
                    <BookingMonitor />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/audit" element={
                <ProtectedRoute>
                  <Layout>
                    <AuditLogs />
                  </Layout>
                </ProtectedRoute>
              } />
            </Routes>
          </Router>
        </ApiProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;