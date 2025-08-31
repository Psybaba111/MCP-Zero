/**
 * Book Ride Screen
 * Pickup and drop location selection with map
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert, Dimensions } from 'react-native';
import { Card, TextInput, Button, Text, IconButton } from 'react-native-paper';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';
import { useNavigation } from '@react-navigation/native';

const { width, height } = Dimensions.get('window');

export default function BookRideScreen() {
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropAddress, setDropAddress] = useState('');
  const [pickupLocation, setPickupLocation] = useState<any>(null);
  const [dropLocation, setDropLocation] = useState<any>(null);
  const [currentLocation, setCurrentLocation] = useState<any>(null);
  const [mapRegion, setMapRegion] = useState({
    latitude: 12.9716,
    longitude: 77.5946,
    latitudeDelta: 0.01,
    longitudeDelta: 0.01,
  });
  const navigation = useNavigation();

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setCurrentLocation(location.coords);
      setMapRegion({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        latitudeDelta: 0.01,
        longitudeDelta: 0.01,
      });
    } catch (error) {
      console.error('Error getting location:', error);
    }
  };

  const handleUseCurrentLocation = () => {
    if (currentLocation) {
      setPickupLocation(currentLocation);
      setPickupAddress('Current Location');
    } else {
      Alert.alert('Error', 'Unable to get current location');
    }
  };

  const handleMapPress = (event: any) => {
    const { latitude, longitude } = event.nativeEvent.coordinate;
    
    if (!pickupLocation) {
      setPickupLocation({ latitude, longitude });
      setPickupAddress(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
    } else if (!dropLocation) {
      setDropLocation({ latitude, longitude });
      setDropAddress(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
    }
  };

  const handleNext = () => {
    if (!pickupLocation || !dropLocation) {
      Alert.alert('Error', 'Please select both pickup and drop locations');
      return;
    }

    const bookingData = {
      pickup_lat: pickupLocation.latitude,
      pickup_lng: pickupLocation.longitude,
      pickup_address: pickupAddress,
      drop_lat: dropLocation.latitude,
      drop_lng: dropLocation.longitude,
      drop_address: dropAddress,
    };

    navigation.navigate('VehicleSelection' as never, { bookingData } as never);
  };

  const clearLocations = () => {
    setPickupLocation(null);
    setDropLocation(null);
    setPickupAddress('');
    setDropAddress('');
  };

  return (
    <View style={styles.container}>
      {/* Map */}
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        region={mapRegion}
        onPress={handleMapPress}
        showsUserLocation={true}
      >
        {pickupLocation && (
          <Marker
            coordinate={pickupLocation}
            title="Pickup Location"
            pinColor="#4CAF50"
          />
        )}
        {dropLocation && (
          <Marker
            coordinate={dropLocation}
            title="Drop Location"
            pinColor="#F44336"
          />
        )}
      </MapView>

      {/* Location Input Card */}
      <Card style={styles.inputCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.cardTitle}>
            Select Locations
          </Text>
          
          <View style={styles.locationInputs}>
            <View style={styles.inputRow}>
              <View style={styles.locationDot} />
              <TextInput
                label="Pickup Location"
                value={pickupAddress}
                onChangeText={setPickupAddress}
                mode="outlined"
                style={styles.locationInput}
                right={
                  <TextInput.Icon 
                    icon="crosshairs-gps" 
                    onPress={handleUseCurrentLocation}
                  />
                }
              />
            </View>
            
            <View style={styles.inputRow}>
              <View style={[styles.locationDot, styles.dropDot]} />
              <TextInput
                label="Drop Location"
                value={dropAddress}
                onChangeText={setDropAddress}
                mode="outlined"
                style={styles.locationInput}
              />
            </View>
          </View>

          <Text variant="bodySmall" style={styles.helpText}>
            Tap on the map to set pickup and drop locations
          </Text>

          <View style={styles.buttonRow}>
            <Button 
              mode="outlined" 
              onPress={clearLocations}
              style={styles.clearButton}
            >
              Clear
            </Button>
            <Button 
              mode="contained" 
              onPress={handleNext}
              style={styles.nextButton}
              disabled={!pickupLocation || !dropLocation}
            >
              Next
            </Button>
          </View>
        </Card.Content>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  map: {
    width: width,
    height: height * 0.6,
  },
  inputCard: {
    position: 'absolute',
    bottom: 20,
    left: 16,
    right: 16,
    elevation: 8,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  cardTitle: {
    marginBottom: 16,
    color: '#333',
  },
  locationInputs: {
    marginBottom: 12,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  locationDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#4CAF50',
    marginRight: 12,
    marginTop: 12,
  },
  dropDot: {
    backgroundColor: '#F44336',
  },
  locationInput: {
    flex: 1,
  },
  helpText: {
    color: '#666',
    textAlign: 'center',
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
  },
  clearButton: {
    flex: 1,
  },
  nextButton: {
    flex: 2,
  },
});