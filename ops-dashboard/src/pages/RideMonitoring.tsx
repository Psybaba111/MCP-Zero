/**
 * Ride Monitoring Page
 * Real-time monitoring of active rides and parcels
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert
} from '@mui/material';
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid';
import { Visibility, Assignment, Cancel } from '@mui/icons-material';

import { useApi } from '../contexts/ApiContext';

export default function RideMonitoring() {
  const [rides, setRides] = useState([]);
  const [parcels, setParcels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRide, setSelectedRide] = useState<any>(null);
  const [assignDriverDialog, setAssignDriverDialog] = useState(false);
  const [driverAssignment, setDriverAssignment] = useState({ driverId: '', notes: '' });
  const { apiCall } = useApi();

  useEffect(() => {
    loadData();
    
    // Refresh every 15 seconds
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [ridesResponse, parcelsResponse] = await Promise.all([
        apiCall('/rides?limit=100'),
        apiCall('/parcels?limit=100')
      ]);
      
      setRides(ridesResponse);
      setParcels(parcelsResponse);
    } catch (error: any) {
      console.error('Failed to load ride data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (entity: any) => {
    setSelectedRide(entity);
  };

  const handleAssignDriver = (ride: any) => {
    setSelectedRide(ride);
    setAssignDriverDialog(true);
  };

  const handleDriverAssignment = async () => {
    try {
      await apiCall(`/rides/${selectedRide.id}/assign`, 'POST', {
        driver_id: driverAssignment.driverId,
        notes: driverAssignment.notes
      });
      
      setAssignDriverDialog(false);
      setDriverAssignment({ driverId: '', notes: '' });
      loadData();
    } catch (error: any) {
      alert('Failed to assign driver: ' + error.message);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      created: 'default',
      paid: 'info',
      assigned: 'success',
      in_progress: 'warning',
      completed: 'success',
      cancelled: 'error'
    } as const;
    return colors[status as keyof typeof colors] || 'default';
  };

  const rideColumns: GridColDef[] = [
    { field: 'id', headerName: 'Ride ID', width: 120, valueGetter: (params) => params.row.id.slice(0, 8) },
    { field: 'passenger_name', headerName: 'Passenger', width: 150, valueGetter: (params) => params.row.passenger?.full_name || 'N/A' },
    { field: 'pickup_address', headerName: 'Pickup', width: 200 },
    { field: 'drop_address', headerName: 'Drop', width: 200 },
    { field: 'vehicle_type', headerName: 'Vehicle', width: 100 },
    { field: 'estimated_fare', headerName: 'Fare', width: 100, valueFormatter: (params) => `₹${params.value}` },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color={getStatusColor(params.value)}
          size="small"
        />
      )
    },
    { field: 'created_at', headerName: 'Created', width: 150, valueFormatter: (params) => new Date(params.value).toLocaleString() },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 150,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<Visibility />}
          label="View"
          onClick={() => handleViewDetails(params.row)}
        />,
        ...(params.row.status === 'paid' ? [
          <GridActionsCellItem
            icon={<Assignment />}
            label="Assign Driver"
            onClick={() => handleAssignDriver(params.row)}
          />
        ] : [])
      ]
    }
  ];

  const parcelColumns: GridColDef[] = [
    { field: 'id', headerName: 'Parcel ID', width: 120, valueGetter: (params) => params.row.id.slice(0, 8) },
    { field: 'sender_name', headerName: 'Sender', width: 150, valueGetter: (params) => params.row.sender?.full_name || 'N/A' },
    { field: 'recipient_name', headerName: 'Recipient', width: 150 },
    { field: 'pickup_address', headerName: 'Pickup', width: 200 },
    { field: 'drop_address', headerName: 'Drop', width: 200 },
    { field: 'estimated_fare', headerName: 'Fare', width: 100, valueFormatter: (params) => `₹${params.value}` },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color={getStatusColor(params.value)}
          size="small"
        />
      )
    },
    { field: 'created_at', headerName: 'Created', width: 150, valueFormatter: (params) => new Date(params.value).toLocaleString() }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Ride Monitoring
      </Typography>
      
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Rides"
            value={rides.filter((r: any) => ['assigned', 'in_progress'].includes(r.status)).length}
            icon={<DirectionsCar sx={{ fontSize: 40 }} />}
            color="#4CAF50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Pending Assignment"
            value={rides.filter((r: any) => r.status === 'paid').length}
            icon={<Assignment sx={{ fontSize: 40 }} />}
            color="#FF9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Deliveries"
            value={parcels.filter((p: any) => ['assigned', 'in_progress'].includes(p.status)).length}
            icon={<LocalShipping sx={{ fontSize: 40 }} />}
            color="#2196F3"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Response Time"
            value={`${metrics.avg_response_time?.toFixed(0) || 0}ms`}
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="#9C27B0"
          />
        </Grid>
      </Grid>

      {/* System Health Alert */}
      {metrics.error_rate > 1 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          High error rate detected ({metrics.error_rate.toFixed(1)}%). Please check system health.
        </Alert>
      )}

      {/* Rides Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Rides
          </Typography>
          <DataGrid
            rows={rides}
            columns={rideColumns}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 10 },
              },
            }}
            pageSizeOptions={[10, 25, 50]}
            loading={loading}
            autoHeight
          />
        </CardContent>
      </Card>

      {/* Parcels Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Parcels
          </Typography>
          <DataGrid
            rows={parcels}
            columns={parcelColumns}
            initialState={{
              pagination: {
                paginationModel: { page: 0, pageSize: 10 },
              },
            }}
            pageSizeOptions={[10, 25, 50]}
            loading={loading}
            autoHeight
          />
        </CardContent>
      </Card>

      {/* Driver Assignment Dialog */}
      <Dialog open={assignDriverDialog} onClose={() => setAssignDriverDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assign Driver to Ride</DialogTitle>
        <DialogContent>
          <TextField
            select
            label="Select Driver"
            value={driverAssignment.driverId}
            onChange={(e) => setDriverAssignment(prev => ({ ...prev, driverId: e.target.value }))}
            fullWidth
            margin="normal"
          >
            <MenuItem value="driver1">John Doe - Car (4.8★)</MenuItem>
            <MenuItem value="driver2">Jane Smith - Bike (4.9★)</MenuItem>
            <MenuItem value="driver3">Mike Johnson - Scooter (4.7★)</MenuItem>
          </TextField>
          
          <TextField
            label="Assignment Notes"
            value={driverAssignment.notes}
            onChange={(e) => setDriverAssignment(prev => ({ ...prev, notes: e.target.value }))}
            fullWidth
            multiline
            rows={3}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDriverDialog(false)}>Cancel</Button>
          <Button onClick={handleDriverAssignment} variant="contained">
            Assign Driver
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}