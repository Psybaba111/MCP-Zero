/**
 * Profile Screen
 * User profile with links to KYC, compliance, and settings
 */

import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Text, Button, Avatar, List, Divider } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

import { useAuth } from '../contexts/AuthContext';

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const navigation = useNavigation();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: logout },
      ]
    );
  };

  const getKYCStatusColor = (status: string) => {
    const colors = {
      pending: '#FF9800',
      in_progress: '#2196F3',
      approved: '#4CAF50',
      rejected: '#F44336'
    };
    return colors[status as keyof typeof colors] || '#999';
  };

  const getKYCStatusIcon = (status: string) => {
    const icons = {
      pending: 'clock-outline',
      in_progress: 'progress-clock',
      approved: 'check-circle',
      rejected: 'close-circle'
    };
    return icons[status as keyof typeof icons] || 'help-circle';
  };

  return (
    <ScrollView style={styles.container}>
      {/* User Info Card */}
      <Card style={styles.userCard}>
        <Card.Content>
          <View style={styles.userHeader}>
            <Avatar.Text 
              size={64} 
              label={user?.full_name?.charAt(0) || 'U'}
              style={styles.avatar}
            />
            <View style={styles.userInfo}>
              <Text variant="headlineSmall" style={styles.userName}>
                {user?.full_name}
              </Text>
              <Text variant="bodyMedium" style={styles.userEmail}>
                {user?.email}
              </Text>
              <Text variant="bodyMedium" style={styles.userPhone}>
                {user?.phone}
              </Text>
              <View style={styles.roleChip}>
                <Text variant="labelMedium" style={styles.roleText}>
                  {user?.role?.toUpperCase()}
                </Text>
              </View>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* KYC Status Card */}
      <Card style={styles.kycCard}>
        <Card.Content>
          <View style={styles.kycHeader}>
            <Text variant="titleMedium">KYC Status</Text>
            <View style={[styles.statusBadge, { backgroundColor: getKYCStatusColor(user?.kyc_status || 'pending') }]}>
              <MaterialCommunityIcons 
                name={getKYCStatusIcon(user?.kyc_status || 'pending')} 
                size={16} 
                color="#fff" 
              />
              <Text variant="labelMedium" style={styles.statusText}>
                {(user?.kyc_status || 'pending').toUpperCase()}
              </Text>
            </View>
          </View>
          
          <Button 
            mode="outlined" 
            style={styles.kycButton}
            onPress={() => navigation.navigate('ComplianceHub' as never)}
          >
            View Compliance Hub
          </Button>
        </Card.Content>
      </Card>

      {/* Menu Items */}
      <Card style={styles.menuCard}>
        <List.Section>
          <List.Item
            title="My Rentals"
            description="View your rental history"
            left={(props) => <List.Icon {...props} icon="car-clock" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('MyRentals' as never)}
          />
          
          <Divider />
          
          <List.Item
            title="My Vehicles"
            description="Manage your listed vehicles"
            left={(props) => <List.Icon {...props} icon="car-multiple" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('MyVehicles' as never)}
          />
          
          <Divider />
          
          <List.Item
            title="License Tracker"
            description="Track document expiry dates"
            left={(props) => <List.Icon {...props} icon="card-account-details" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('LicenseTracker' as never)}
          />
          
          <Divider />
          
          <List.Item
            title="Consent Settings"
            description="Manage your privacy preferences"
            left={(props) => <List.Icon {...props} icon="shield-account" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('ConsentSettings' as never)}
          />
          
          <Divider />
          
          <List.Item
            title="Support"
            description="Get help and contact support"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Support', 'Support feature coming soon!')}
          />
        </List.Section>
      </Card>

      {/* Logout Button */}
      <Card style={styles.logoutCard}>
        <Card.Content>
          <Button 
            mode="outlined" 
            onPress={handleLogout}
            icon="logout"
            textColor="#F44336"
            style={styles.logoutButton}
          >
            Logout
          </Button>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  userCard: {
    margin: 16,
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  avatar: {
    backgroundColor: '#4CAF50',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    color: '#333',
    marginBottom: 4,
  },
  userEmail: {
    color: '#666',
    marginBottom: 2,
  },
  userPhone: {
    color: '#666',
    marginBottom: 8,
  },
  roleChip: {
    backgroundColor: '#E8F5E8',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  roleText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  kycCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  kycHeader: {
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
  kycButton: {
    marginTop: 8,
  },
  menuCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  logoutCard: {
    marginHorizontal: 16,
    marginBottom: 32,
    elevation: 2,
  },
  logoutButton: {
    borderColor: '#F44336',
  },
});