/**
 * Booking Confirmation Screen
 * Shows booking success with tracking info
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Card, Text, Button, ActivityIndicator, Divider } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRoute, useNavigation } from '@react-navigation/native';

import { useApi } from '../../contexts/ApiContext';

export default function BookingConfirmationScreen() {
  const [entity, setEntity] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const route = useRoute();
  const navigation = useNavigation();
  const { apiCall } = useApi();
  
  const { entityType, entityId } = route.params as any;

  useEffect(() => {
    loadEntityDetails();
  }, []);

  const loadEntityDetails = async () => {
    try {
      setLoading(true);
      const response = await apiCall(`/${entityType}s/${entityId}`);
      setEntity(response);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load booking details');
    } finally {
      setLoading(false);
    }
  };

  const handleGoHome = () => {
    navigation.navigate('Home' as never);
  };

  const getStatusColor = (status: string) => {
    const colors = {
      created: '#FF9800',
      paid: '#2196F3',
      assigned: '#4CAF50',
      in_progress: '#9C27B0',
      completed: '#4CAF50'
    };
    return colors[status as keyof typeof colors] || '#999';
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      created: 'clock-outline',
      paid: 'check-circle',
      assigned: 'account-check',
      in_progress: 'car',
      completed: 'check-all'
    };
    return icons[status as keyof typeof icons] || 'help-circle';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Loading booking details...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Success Header */}
      <View style={styles.successHeader}>
        <MaterialCommunityIcons name="check-circle" size={64} color="#4CAF50" />
        <Text variant="headlineMedium" style={styles.successTitle}>
          Booking Confirmed!
        </Text>
        <Text variant="bodyLarge" style={styles.successSubtitle}>
          Your {entityType} has been booked successfully
        </Text>
      </View>

      {/* Booking Details Card */}
      <Card style={styles.detailsCard}>
        <Card.Content>
          <View style={styles.statusRow}>
            <Text variant="titleMedium">Status</Text>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(entity?.status || 'created') }]}>
              <MaterialCommunityIcons 
                name={getStatusIcon(entity?.status || 'created')} 
                size={16} 
                color="#fff" 
              />
              <Text variant="labelMedium" style={styles.statusText}>
                {(entity?.status || 'created').toUpperCase()}
              </Text>
            </View>
          </View>
          
          <Divider style={styles.divider} />
          
          <View style={styles.detailRow}>
            <Text variant="bodyMedium">Booking ID:</Text>
            <Text variant="bodyMedium" style={styles.detailValue}>
              {entity?.id?.slice(0, 8)}...
            </Text>
          </View>
          
          {entityType === 'ride' && (
            <>
              <View style={styles.detailRow}>
                <Text variant="bodyMedium">Vehicle Type:</Text>
                <Text variant="bodyMedium" style={styles.detailValue}>
                  {entity?.vehicle_type}
                </Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text variant="bodyMedium">Estimated Fare:</Text>
                <Text variant="bodyMedium" style={styles.detailValue}>
                  ₹{entity?.estimated_fare}
                </Text>
              </View>
            </>
          )}
          
          {entityType === 'rental' && (
            <>
              <View style={styles.detailRow}>
                <Text variant="bodyMedium">Duration:</Text>
                <Text variant="bodyMedium" style={styles.detailValue}>
                  {Math.round((new Date(entity?.end_time).getTime() - new Date(entity?.start_time).getTime()) / (1000 * 60 * 60))} hours
                </Text>
              </View>
              
              <View style={styles.detailRow}>
                <Text variant="bodyMedium">Total Amount:</Text>
                <Text variant="bodyMedium" style={styles.detailValue}>
                  ₹{entity?.total_amount}
                </Text>
              </View>
            </>
          )}
        </Card.Content>
      </Card>

      {/* Driver Assignment Card (for rides) */}
      {entityType === 'ride' && entity?.status === 'assigned' && (
        <Card style={styles.driverCard}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.driverTitle}>
              Driver Assigned
            </Text>
            
            <View style={styles.driverInfo}>
              <MaterialCommunityIcons name="account-circle" size={48} color="#4CAF50" />
              <View style={styles.driverDetails}>
                <Text variant="titleMedium">Driver Name</Text>
                <Text variant="bodyMedium" style={styles.driverPhone}>
                  +91 98765 43210
                </Text>
                <Text variant="bodySmall" style={styles.driverEta}>
                  Arriving in 5 minutes
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* Next Steps */}
      <Card style={styles.nextStepsCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.nextStepsTitle}>
            What's Next?
          </Text>
          
          {entityType === 'ride' && (
            <Text variant="bodyMedium" style={styles.nextStepsText}>
              • We're finding a driver for you{'\n'}
              • You'll get notified when assigned{'\n'}
              • Track your ride in real-time
            </Text>
          )}
          
          {entityType === 'parcel' && (
            <Text variant="bodyMedium" style={styles.nextStepsText}>
              • We're finding a delivery partner{'\n'}
              • You'll get pickup confirmation{'\n'}
              • Track delivery in real-time
            </Text>
          )}
          
          {entityType === 'rental' && (
            <Text variant="bodyMedium" style={styles.nextStepsText}>
              • Your booking is confirmed{'\n'}
              • Vehicle location will be shared{'\n'}
              • Remember to return on time for bonus points
            </Text>
          )}
        </Card.Content>
      </Card>

      {/* Action Buttons */}
      <View style={styles.buttonContainer}>
        <Button
          mode="outlined"
          onPress={handleGoHome}
          style={styles.homeButton}
        >
          Go Home
        </Button>
        
        <Button
          mode="contained"
          onPress={() => navigation.navigate('TrackBooking' as never, { entityType, entityId } as never)}
          style={styles.trackButton}
        >
          Track {entityType === 'ride' ? 'Ride' : entityType === 'parcel' ? 'Parcel' : 'Rental'}
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    color: '#666',
  },
  successHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  successTitle: {
    color: '#333',
    textAlign: 'center',
    marginTop: 16,
  },
  successSubtitle: {
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  detailsCard: {
    marginBottom: 16,
    elevation: 4,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  divider: {
    marginVertical: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailValue: {
    color: '#666',
    fontWeight: '500',
  },
  driverCard: {
    marginBottom: 16,
    elevation: 4,
  },
  driverTitle: {
    marginBottom: 16,
    color: '#333',
  },
  driverInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  driverDetails: {
    flex: 1,
  },
  driverPhone: {
    color: '#666',
    marginTop: 2,
  },
  driverEta: {
    color: '#4CAF50',
    marginTop: 4,
  },
  nextStepsCard: {
    marginBottom: 24,
    elevation: 2,
  },
  nextStepsTitle: {
    marginBottom: 12,
    color: '#333',
  },
  nextStepsText: {
    color: '#666',
    lineHeight: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  homeButton: {
    flex: 1,
  },
  trackButton: {
    flex: 1,
  },
});