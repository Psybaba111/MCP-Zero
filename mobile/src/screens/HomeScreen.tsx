/**
 * Home Screen
 * Map view with Book Ride and Send Parcel options
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert, Dimensions } from 'react-native';
import { Card, Button, Text, FAB, Portal } from 'react-native-paper';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';
import { useNavigation } from '@react-navigation/native';

import { useAuth } from '../contexts/AuthContext';

const { width, height } = Dimensions.get('window');

export default function HomeScreen() {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [fabOpen, setFabOpen] = useState(false);
  const { user } = useAuth();
  const navigation = useNavigation();

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission denied', 'Location permission is required for this app');
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({});
      setLocation(currentLocation);
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Error', 'Failed to get your location');
    }
  };

  const handleBookRide = () => {
    setFabOpen(false);
    navigation.navigate('BookRide' as never);
  };

  const handleSendParcel = () => {
    setFabOpen(false);
    navigation.navigate('SendParcel' as never);
  };

  const region = location ? {
    latitude: location.coords.latitude,
    longitude: location.coords.longitude,
    latitudeDelta: 0.01,
    longitudeDelta: 0.01,
  } : {
    latitude: 12.9716, // Default to Bangalore
    longitude: 77.5946,
    latitudeDelta: 0.01,
    longitudeDelta: 0.01,
  };

  return (
    <View style={styles.container}>
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        region={region}
        showsUserLocation={true}
        showsMyLocationButton={true}
      >
        {location && (
          <Marker
            coordinate={{
              latitude: location.coords.latitude,
              longitude: location.coords.longitude,
            }}
            title="Your Location"
          />
        )}
      </MapView>

      {/* Welcome Card */}
      <Card style={styles.welcomeCard}>
        <Card.Content>
          <Text variant="headlineSmall">Welcome back, {user?.full_name?.split(' ')[0]}!</Text>
          <Text variant="bodyMedium" style={{ marginTop: 4 }}>
            Where would you like to go today?
          </Text>
        </Card.Content>
      </Card>

      {/* Quick Actions FAB */}
      <Portal>
        <FAB.Group
          open={fabOpen}
          visible
          icon={fabOpen ? 'close' : 'plus'}
          actions={[
            {
              icon: 'car',
              label: 'Book Ride',
              onPress: handleBookRide,
            },
            {
              icon: 'package-variant',
              label: 'Send Parcel',
              onPress: handleSendParcel,
            },
          ]}
          onStateChange={({ open }) => setFabOpen(open)}
          style={styles.fab}
        />
      </Portal>

      {/* Quick Stats Cards */}
      <View style={styles.statsContainer}>
        <Card style={styles.statCard}>
          <Card.Content>
            <Text variant="bodySmall">Recent Rides</Text>
            <Text variant="headlineSmall">5</Text>
          </Card.Content>
        </Card>
        
        <Card style={styles.statCard}>
          <Card.Content>
            <Text variant="bodySmall">Reward Points</Text>
            <Text variant="headlineSmall">250</Text>
          </Card.Content>
        </Card>
      </View>
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
  welcomeCard: {
    position: 'absolute',
    top: 20,
    left: 16,
    right: 16,
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  fab: {
    position: 'absolute',
    bottom: 100,
    right: 16,
  },
  statsContainer: {
    position: 'absolute',
    bottom: 20,
    left: 16,
    right: 16,
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
});