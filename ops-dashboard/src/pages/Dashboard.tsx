/**
 * Main Dashboard Page
 * Overview of key metrics and recent activity
 */

import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  DirectionsCar,
  LocalShipping,
  ElectricCar,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

import { useApi } from '../contexts/ApiContext';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
  trend?: number;
}

function MetricCard({ title, value, subtitle, icon, color, trend }: MetricCardProps) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ color }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography color="textSecondary" variant="body2">
                {subtitle}
              </Typography>
            )}
            {trend !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp fontSize="small" sx={{ color: trend > 0 ? 'green' : 'red', mr: 0.5 }} />
                <Typography variant="body2" sx={{ color: trend > 0 ? 'green' : 'red' }}>
                  {trend > 0 ? '+' : ''}{trend}% from yesterday
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color, opacity: 0.8 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>({});
  const [recentActivity, setRecentActivity] = useState([]);
  const [systemHealth, setSystemHealth] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const { apiCall } = useApi();

  useEffect(() => {
    loadDashboardData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [metricsResponse, healthResponse, auditResponse] = await Promise.all([
        apiCall('/metrics'),
        apiCall('/health'),
        apiCall('/audit?limit=10')
      ]);
      
      setMetrics(metricsResponse.metrics);
      setSystemHealth(healthResponse);
      setRecentActivity(auditResponse);
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (status: string) => {
    return status === 'connected' ? 'success' : 'error';
  };

  const getHealthIcon = (status: string) => {
    return status === 'connected' ? <CheckCircle /> : <Error />;
  };

  if (loading) {
    return <LinearProgress />;
  }

  // Mock data for charts
  const rideData = [
    { name: 'Mon', rides: 45, parcels: 12 },
    { name: 'Tue', rides: 52, parcels: 18 },
    { name: 'Wed', rides: 38, parcels: 15 },
    { name: 'Thu', rides: 61, parcels: 22 },
    { name: 'Fri', rides: 73, parcels: 28 },
    { name: 'Sat', rides: 89, parcels: 35 },
    { name: 'Sun', rides: 67, parcels: 19 },
  ];

  const rentalData = [
    { name: 'Cars', count: 25 },
    { name: 'Bikes', count: 45 },
    { name: 'Scooters', count: 67 },
    { name: 'Cycles', count: 23 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Operations Dashboard
      </Typography>
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Rides"
            value={metrics.request_count || 0}
            subtitle="Currently in progress"
            icon={<DirectionsCar sx={{ fontSize: 40 }} />}
            color="#4CAF50"
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Pending Approvals"
            value={15}
            subtitle="Vehicle listings"
            icon={<CheckCircle sx={{ fontSize: 40 }} />}
            color="#FF9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Rentals"
            value={28}
            subtitle="Currently rented"
            icon={<ElectricCar sx={{ fontSize: 40 }} />}
            color="#2196F3"
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Error Rate"
            value={`${metrics.error_rate?.toFixed(1) || 0}%`}
            subtitle="Last 24 hours"
            icon={<Warning sx={{ fontSize: 40 }} />}
            color={metrics.error_rate > 1 ? "#F44336" : "#4CAF50"}
            trend={-2}
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Rides & Parcels (Last 7 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={rideData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="rides" stroke="#4CAF50" strokeWidth={2} />
                  <Line type="monotone" dataKey="parcels" stroke="#2196F3" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Rentals by Type
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={rentalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4CAF50" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Health & Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              <List>
                {Object.entries(systemHealth.services || {}).map(([service, status]) => (
                  <ListItem key={service}>
                    <ListItemIcon>
                      {getHealthIcon(status as string)}
                    </ListItemIcon>
                    <ListItemText 
                      primary={service.charAt(0).toUpperCase() + service.slice(1)}
                      secondary={status as string}
                    />
                    <Chip
                      label={status as string}
                      color={getHealthColor(status as string)}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
              
              {metrics.avg_response_time && (
                <Box mt={2}>
                  <Typography variant="body2" color="textSecondary">
                    Avg Response Time: {metrics.avg_response_time.toFixed(0)}ms
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    P95 Response Time: {metrics.p95_response_time.toFixed(0)}ms
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {recentActivity.slice(0, 5).map((activity: any) => (
                  <ListItem key={activity.id}>
                    <ListItemText
                      primary={activity.event_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      secondary={`${activity.action} • ${new Date(activity.created_at).toLocaleTimeString()}`}
                    />
                    <Chip
                      label={activity.entity_type}
                      size="small"
                      variant="outlined"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}