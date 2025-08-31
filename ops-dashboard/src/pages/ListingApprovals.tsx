/**
 * Listing Approvals Page
 * Vehicle listing approval workflow for ops team
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
  ImageList,
  ImageListItem,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import { DataGrid, GridColDef, GridActionsCellItem } from '@mui/x-data-grid';
import { Visibility, CheckCircle, Cancel, Warning } from '@mui/icons-material';

import { useApi } from '../contexts/ApiContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`approval-tabpanel-${index}`}
      aria-labelledby={`approval-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function ListingApprovals() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVehicle, setSelectedVehicle] = useState<any>(null);
  const [viewDialog, setViewDialog] = useState(false);
  const [approvalDialog, setApprovalDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const { apiCall } = useApi();

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/vehicles?available_only=false');
      setVehicles(response);
    } catch (error: any) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (vehicle: any) => {
    setSelectedVehicle(vehicle);
    setViewDialog(true);
  };

  const handleApprove = async (vehicleId: string) => {
    try {
      await apiCall(`/vehicles/${vehicleId}/approve`, 'POST');
      loadVehicles();
    } catch (error: any) {
      alert('Failed to approve vehicle: ' + error.message);
    }
  };

  const handleReject = (vehicle: any) => {
    setSelectedVehicle(vehicle);
    setApprovalDialog(true);
  };

  const handleRejectConfirm = async () => {
    try {
      await apiCall(`/vehicles/${selectedVehicle.id}`, 'PUT', {
        status: 'rejected',
        rejection_reason: rejectionReason
      });
      
      setApprovalDialog(false);
      setRejectionReason('');
      setSelectedVehicle(null);
      loadVehicles();
    } catch (error: any) {
      alert('Failed to reject vehicle: ' + error.message);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'warning',
      approved: 'success',
      rejected: 'error',
      active: 'info',
      inactive: 'default'
    } as const;
    return colors[status as keyof typeof colors] || 'default';
  };

  const filterVehiclesByStatus = (status: string) => {
    return vehicles.filter((vehicle: any) => vehicle.status === status);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 120, valueGetter: (params) => params.row.id.slice(0, 8) },
    { field: 'owner_name', headerName: 'Owner', width: 150, valueGetter: (params) => params.row.owner?.full_name || 'N/A' },
    { 
      field: 'vehicle_info', 
      headerName: 'Vehicle', 
      width: 200,
      valueGetter: (params) => `${params.row.make} ${params.row.model} ${params.row.year || ''}`
    },
    { field: 'vehicle_type', headerName: 'Type', width: 100 },
    { field: 'registration_number', headerName: 'Registration', width: 130 },
    { field: 'hourly_rate', headerName: 'Rate/hr', width: 100, valueFormatter: (params) => `₹${params.value}` },
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
    { field: 'created_at', headerName: 'Submitted', width: 150, valueFormatter: (params) => new Date(params.value).toLocaleDateString() },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 200,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<Visibility />}
          label="View Details"
          onClick={() => handleViewDetails(params.row)}
        />,
        ...(params.row.status === 'pending' ? [
          <GridActionsCellItem
            icon={<CheckCircle />}
            label="Approve"
            onClick={() => handleApprove(params.row.id)}
            showInMenu
          />,
          <GridActionsCellItem
            icon={<Cancel />}
            label="Reject"
            onClick={() => handleReject(params.row)}
            showInMenu
          />
        ] : [])
      ]
    }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Vehicle Listing Approvals
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Approval
              </Typography>
              <Typography variant="h4" sx={{ color: '#FF9800' }}>
                {filterVehiclesByStatus('pending').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Approved Today
              </Typography>
              <Typography variant="h4" sx={{ color: '#4CAF50' }}>
                {filterVehiclesByStatus('approved').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Rejected
              </Typography>
              <Typography variant="h4" sx={{ color: '#F44336' }}>
                {filterVehiclesByStatus('rejected').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Active
              </Typography>
              <Typography variant="h4" sx={{ color: '#2196F3' }}>
                {filterVehiclesByStatus('active').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for different statuses */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label={`Pending (${filterVehiclesByStatus('pending').length})`} />
            <Tab label={`Approved (${filterVehiclesByStatus('approved').length})`} />
            <Tab label={`Rejected (${filterVehiclesByStatus('rejected').length})`} />
            <Tab label="All Vehicles" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <DataGrid
            rows={filterVehiclesByStatus('pending')}
            columns={columns}
            initialState={{
              pagination: { paginationModel: { page: 0, pageSize: 25 } },
            }}
            pageSizeOptions={[25, 50, 100]}
            loading={loading}
            autoHeight
          />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <DataGrid
            rows={filterVehiclesByStatus('approved')}
            columns={columns}
            initialState={{
              pagination: { paginationModel: { page: 0, pageSize: 25 } },
            }}
            pageSizeOptions={[25, 50, 100]}
            loading={loading}
            autoHeight
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <DataGrid
            rows={filterVehiclesByStatus('rejected')}
            columns={columns}
            initialState={{
              pagination: { paginationModel: { page: 0, pageSize: 25 } },
            }}
            pageSizeOptions={[25, 50, 100]}
            loading={loading}
            autoHeight
          />
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <DataGrid
            rows={vehicles}
            columns={columns}
            initialState={{
              pagination: { paginationModel: { page: 0, pageSize: 25 } },
            }}
            pageSizeOptions={[25, 50, 100]}
            loading={loading}
            autoHeight
          />
        </TabPanel>
      </Card>

      {/* Vehicle Details Dialog */}
      <Dialog open={viewDialog} onClose={() => setViewDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Vehicle Details - {selectedVehicle?.make} {selectedVehicle?.model}
        </DialogTitle>
        <DialogContent>
          {selectedVehicle && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Vehicle Information</Typography>
                <Typography>Make: {selectedVehicle.make}</Typography>
                <Typography>Model: {selectedVehicle.model}</Typography>
                <Typography>Year: {selectedVehicle.year}</Typography>
                <Typography>Type: {selectedVehicle.vehicle_type}</Typography>
                <Typography>Registration: {selectedVehicle.registration_number}</Typography>
                <Typography>Battery: {selectedVehicle.battery_capacity || 'N/A'} kWh</Typography>
                <Typography>Range: {selectedVehicle.range_km || 'N/A'} km</Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Pricing</Typography>
                <Typography>Hourly Rate: ₹{selectedVehicle.hourly_rate}</Typography>
                <Typography>Daily Rate: ₹{selectedVehicle.daily_rate}</Typography>
                <Typography>Deposit: ₹{selectedVehicle.deposit_amount}</Typography>
                
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>Status</Typography>
                <Chip 
                  label={selectedVehicle.status} 
                  color={getStatusColor(selectedVehicle.status)}
                />
              </Grid>
              
              {selectedVehicle.photos && selectedVehicle.photos.length > 0 && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>Photos</Typography>
                  <ImageList cols={3} rowHeight={164}>
                    {selectedVehicle.photos.map((photo: string, index: number) => (
                      <ImageListItem key={index}>
                        <img src={photo} alt={`Vehicle ${index + 1}`} loading="lazy" />
                      </ImageListItem>
                    ))}
                  </ImageList>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>Close</Button>
          {selectedVehicle?.status === 'pending' && (
            <>
              <Button onClick={() => handleReject(selectedVehicle)} color="error">
                Reject
              </Button>
              <Button onClick={() => handleApprove(selectedVehicle.id)} variant="contained">
                Approve
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Rejection Dialog */}
      <Dialog open={approvalDialog} onClose={() => setApprovalDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reject Vehicle Listing</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action will reject the vehicle listing. The owner will be notified.
          </Alert>
          <TextField
            label="Rejection Reason"
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            fullWidth
            multiline
            rows={4}
            required
            helperText="Please provide a clear reason for rejection"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleRejectConfirm} 
            color="error" 
            variant="contained"
            disabled={!rejectionReason.trim()}
          >
            Reject Listing
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}