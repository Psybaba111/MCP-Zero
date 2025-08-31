/**
 * Vehicle Selection Screen
 * Choose vehicle type and see fare estimate
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, Alert } from 'react-native';
import { Card, Text, Button, ActivityIndicator, RadioButton } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRoute, useNavigation } from '@react-navigation/native';

import { useApi } from '../../contexts/ApiContext';

const VEHICLE_TYPES = [
  {
    key: 'cycle',
    name: 'Cycle',
    icon: 'bicycle',
    description: 'Eco-friendly for short distances',
    color: '#4CAF50'
  },
  {
    key: 'scooter',
    name: 'E-Scooter',
    icon: 'scooter',
    description: 'Quick and efficient',
    color: '#2196F3'
  },
  {
    key: 'bike',
    name: 'E-Bike',
    icon: 'motorbike',
    description: 'Fast and reliable',
    color: '#FF9800'
  },
  {
    key: 'car',
    name: 'E-Car',
    icon: 'car-electric',
    description: 'Comfortable for longer trips',
    color: '#9C27B0'
  },
];

export default function VehicleSelectionScreen() {
  const [selectedVehicle, setSelectedVehicle] = useState('scooter');
  const [fareEstimates, setFareEstimates] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const route = useRoute();
  const navigation = useNavigation();
  const { apiCall } = useApi();
  
  const { bookingData } = route.params as any;

  useEffect(() => {
    calculateFares();
  }, []);

  const calculateFares = async () => {
    try {
      setLoading(true);
      const estimates: any = {};
      
      // Calculate fare for each vehicle type
      for (const vehicleType of VEHICLE_TYPES) {
        try {
          // Mock fare calculation - in real app, call backend API
          const distance = calculateDistance(
            bookingData.pickup_lat,
            bookingData.pickup_lng,
            bookingData.drop_lat,
            bookingData.drop_lng
          );
          
          const baseFares = { cycle: 10, scooter: 20, bike: 30, car: 50 };
          const ratePerKm = { cycle: 5, scooter: 8, bike: 12, car: 15 };
          
          const baseFare = baseFares[vehicleType.key as keyof typeof baseFares];
          const distanceFare = distance * ratePerKm[vehicleType.key as keyof typeof ratePerKm];
          const totalFare = Math.max(baseFare + distanceFare, baseFare * 2);
          
          estimates[vehicleType.key] = {
            fare: Math.round(totalFare),
            distance: distance.toFixed(1),
            eta: Math.round(distance * 3) // Rough ETA calculation
          };
        } catch (error) {
          estimates[vehicleType.key] = { fare: 0, distance: '0', eta: 0 };
        }
      }
      
      setFareEstimates(estimates);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to calculate fare estimates');
    } finally {
      setLoading(false);
    }
  };

  const calculateDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  const handleProceedToPay = () => {
    const selectedVehicleData = VEHICLE_TYPES.find(v => v.key === selectedVehicle);
    const fareData = fareEstimates[selectedVehicle];
    
    if (!fareData) {
      Alert.alert('Error', 'Fare estimate not available');
      return;
    }

    const finalBookingData = {
      ...bookingData,
      vehicle_type: selectedVehicle,
      estimated_fare: fareData.fare
    };

    navigation.navigate('PaymentSheet' as never, { 
      bookingData: finalBookingData,
      entityType: 'ride'
    } as never);
  };

  const renderVehicleOption = ({ item: vehicle }: { item: any }) => {
    const fareData = fareEstimates[vehicle.key];
    const isSelected = selectedVehicle === vehicle.key;

    return (
      <Card 
        style={[styles.vehicleCard, isSelected && styles.selectedCard]}
        onPress={() => setSelectedVehicle(vehicle.key)}
      >
        <Card.Content>
          <View style={styles.vehicleHeader}>
            <View style={styles.vehicleInfo}>
              <MaterialCommunityIcons 
                name={vehicle.icon} 
                size={32} 
                color={vehicle.color}
              />
              <View style={styles.vehicleText}>
                <Text variant="titleMedium" style={styles.vehicleName}>
                  {vehicle.name}
                </Text>
                <Text variant="bodySmall" style={styles.vehicleDescription}>
                  {vehicle.description}
                </Text>
              </View>
            </View>
            
            <RadioButton
              value={vehicle.key}
              status={isSelected ? 'checked' : 'unchecked'}
              onPress={() => setSelectedVehicle(vehicle.key)}
            />
          </View>
          
          {fareData && (
            <View style={styles.fareInfo}>
              <View style={styles.fareDetails}>
                <Text variant="bodySmall" style={styles.fareLabel}>
                  Distance: {fareData.distance} km
                </Text>
                <Text variant="bodySmall" style={styles.fareLabel}>
                  ETA: {fareData.eta} min
                </Text>
              </View>
              <Text variant="titleLarge" style={styles.fare}>
                ₹{fareData.fare}
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Calculating fares...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Trip Summary */}
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.summaryTitle}>
            Trip Summary
          </Text>
          
          <View style={styles.locationRow}>
            <View style={styles.pickupDot} />
            <Text variant="bodyMedium" numberOfLines={1} style={styles.locationText}>
              {bookingData.pickup_address}
            </Text>
          </View>
          
          <View style={styles.locationRow}>
            <View style={styles.dropDot} />
            <Text variant="bodyMedium" numberOfLines={1} style={styles.locationText}>
              {bookingData.drop_address}
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Vehicle Options */}
      <FlatList
        data={VEHICLE_TYPES}
        keyExtractor={(item) => item.key}
        renderItem={renderVehicleOption}
        contentContainerStyle={styles.vehiclesList}
        showsVerticalScrollIndicator={false}
      />

      {/* Proceed Button */}
      <View style={styles.bottomContainer}>
        <Button
          mode="contained"
          onPress={handleProceedToPay}
          style={styles.proceedButton}
          disabled={!selectedVehicle || !fareEstimates[selectedVehicle]}
        >
          Proceed to Pay • ₹{fareEstimates[selectedVehicle]?.fare || 0}
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  summaryCard: {
    margin: 16,
    elevation: 2,
  },
  summaryTitle: {
    marginBottom: 12,
    color: '#333',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  pickupDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#4CAF50',
    marginRight: 12,
  },
  dropDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#F44336',
    marginRight: 12,
  },
  locationText: {
    flex: 1,
    color: '#666',
  },
  vehiclesList: {
    padding: 16,
    gap: 12,
  },
  vehicleCard: {
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  selectedCard: {
    borderColor: '#4CAF50',
    borderWidth: 2,
  },
  vehicleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  vehicleInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  vehicleText: {
    marginLeft: 12,
    flex: 1,
  },
  vehicleName: {
    color: '#333',
  },
  vehicleDescription: {
    color: '#666',
    marginTop: 2,
  },
  fareInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  fareDetails: {
    flex: 1,
  },
  fareLabel: {
    color: '#666',
  },
  fare: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  bottomContainer: {
    padding: 16,
    backgroundColor: '#fff',
    elevation: 8,
  },
  proceedButton: {
    paddingVertical: 4,
  },
});