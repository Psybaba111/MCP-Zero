/**
 * Rent EV Screen
 * P2P vehicle rental marketplace with category tabs
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, Alert } from 'react-native';
import { Card, Text, Button, Chip, SearchBar, ActivityIndicator } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

import { useApi } from '../contexts/ApiContext';

const VEHICLE_CATEGORIES = [
  { key: 'car', label: 'Cars', icon: 'car' },
  { key: 'bike', label: 'Bikes', icon: 'motorbike' },
  { key: 'scooter', label: 'Scooters', icon: 'scooter' },
  { key: 'cycle', label: 'Cycles', icon: 'bicycle' },
];

export default function RentEVScreen() {
  const [selectedCategory, setSelectedCategory] = useState('car');
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { apiCall } = useApi();
  const navigation = useNavigation();

  useEffect(() => {
    loadVehicles();
  }, [selectedCategory]);

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const response = await apiCall(
        `/vehicles?vehicle_type=${selectedCategory}&available_only=true`
      );
      setVehicles(response);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load vehicles');
    } finally {
      setLoading(false);
    }
  };

  const handleVehiclePress = (vehicle: any) => {
    navigation.navigate('VehicleDetail' as never, { vehicle } as never);
  };

  const renderVehicleCard = ({ item: vehicle }: { item: any }) => (
    <Card style={styles.vehicleCard} onPress={() => handleVehiclePress(vehicle)}>
      <Card.Cover 
        source={{ uri: vehicle.photos?.[0] || 'https://via.placeholder.com/300x200' }}
        style={styles.vehicleImage}
      />
      <Card.Content>
        <Text variant="titleMedium" style={styles.vehicleName}>
          {vehicle.make} {vehicle.model} {vehicle.year}
        </Text>
        
        <View style={styles.vehicleDetails}>
          <View style={styles.detailRow}>
            <MaterialCommunityIcons name="battery" size={16} color="#4CAF50" />
            <Text variant="bodySmall" style={styles.detailText}>
              {vehicle.range_km || 'N/A'} km range
            </Text>
          </View>
          
          <View style={styles.detailRow}>
            <MaterialCommunityIcons name="map-marker" size={16} color="#666" />
            <Text variant="bodySmall" style={styles.detailText}>
              2.5 km away
            </Text>
          </View>
        </View>
        
        <View style={styles.priceRow}>
          <Text variant="titleMedium" style={styles.price}>
            ₹{vehicle.hourly_rate}/hr
          </Text>
          <Text variant="bodySmall" style={styles.dailyPrice}>
            ₹{vehicle.daily_rate}/day
          </Text>
        </View>
        
        <View style={styles.features}>
          {vehicle.features?.slice(0, 3).map((feature: string, index: number) => (
            <Chip key={index} compact style={styles.featureChip}>
              {feature}
            </Chip>
          ))}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      {/* Category Tabs */}
      <View style={styles.categoryContainer}>
        <FlatList
          horizontal
          showsHorizontalScrollIndicator={false}
          data={VEHICLE_CATEGORIES}
          keyExtractor={(item) => item.key}
          renderItem={({ item }) => (
            <Chip
              selected={selectedCategory === item.key}
              onPress={() => setSelectedCategory(item.key)}
              style={styles.categoryChip}
              icon={item.icon}
            >
              {item.label}
            </Chip>
          )}
          contentContainerStyle={styles.categoryList}
        />
      </View>

      {/* Search Bar */}
      <SearchBar
        placeholder="Search vehicles..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchBar}
      />

      {/* Vehicles List */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4CAF50" />
          <Text style={styles.loadingText}>Loading vehicles...</Text>
        </View>
      ) : (
        <FlatList
          data={vehicles}
          keyExtractor={(item: any) => item.id}
          renderItem={renderVehicleCard}
          contentContainerStyle={styles.vehiclesList}
          showsVerticalScrollIndicator={false}
          onRefresh={loadVehicles}
          refreshing={loading}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  categoryContainer: {
    backgroundColor: '#fff',
    paddingVertical: 12,
    elevation: 2,
  },
  categoryList: {
    paddingHorizontal: 16,
    gap: 8,
  },
  categoryChip: {
    marginRight: 8,
  },
  searchBar: {
    margin: 16,
    elevation: 2,
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
  vehiclesList: {
    padding: 16,
    gap: 16,
  },
  vehicleCard: {
    elevation: 3,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  vehicleImage: {
    height: 200,
  },
  vehicleName: {
    marginBottom: 8,
    color: '#333',
  },
  vehicleDetails: {
    marginBottom: 12,
    gap: 4,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  detailText: {
    color: '#666',
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  price: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  dailyPrice: {
    color: '#666',
  },
  features: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  featureChip: {
    height: 24,
  },
});