/**
 * EV Opportunities Screen (Coming Soon)
 * Placeholder for future EV opportunity features
 */

import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Card, Button, Text } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';

import { useApi } from '../contexts/ApiContext';
import { useAuth } from '../contexts/AuthContext';

export default function EVOpportunitiesScreen() {
  const [notifyRequested, setNotifyRequested] = useState(false);
  const [loading, setLoading] = useState(false);
  const { apiCall } = useApi();
  const { user } = useAuth();

  const handleNotifyMe = async () => {
    try {
      setLoading(true);
      
      // POST to notify endpoint (placeholder)
      await apiCall('/notifications/ev-opportunities', 'POST', {
        user_id: user?.id,
        feature: 'ev_opportunities',
        timestamp: new Date().toISOString()
      });
      
      setNotifyRequested(true);
      Alert.alert(
        'Success!', 
        'We\'ll notify you when EV Opportunities become available!'
      );
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to register notification');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Card style={styles.comingSoonCard}>
        <Card.Content style={styles.cardContent}>
          <MaterialCommunityIcons 
            name="lightning-bolt" 
            size={64} 
            color="#4CAF50" 
            style={styles.icon}
          />
          
          <Text variant="headlineMedium" style={styles.title}>
            EV Opportunities
          </Text>
          
          <Text variant="bodyLarge" style={styles.subtitle}>
            Coming Soon!
          </Text>
          
          <Text variant="bodyMedium" style={styles.description}>
            Discover exciting opportunities in the EV ecosystem:
          </Text>
          
          <View style={styles.featuresList}>
            <Text variant="bodyMedium" style={styles.feature}>
              ⚡ Partner with charging stations
            </Text>
            <Text variant="bodyMedium" style={styles.feature}>
              🏪 Become a service hub
            </Text>
            <Text variant="bodyMedium" style={styles.feature}>
              💼 Join as a fleet partner
            </Text>
            <Text variant="bodyMedium" style={styles.feature}>
              📈 Investment opportunities
            </Text>
          </View>
          
          {!notifyRequested ? (
            <Button
              mode="contained"
              onPress={handleNotifyMe}
              loading={loading}
              disabled={loading}
              style={styles.notifyButton}
              icon="bell-outline"
            >
              Notify Me When Available
            </Button>
          ) : (
            <Button
              mode="contained-tonal"
              disabled
              style={styles.notifyButton}
              icon="check"
            >
              We'll Notify You!
            </Button>
          )}
        </Card.Content>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
    justifyContent: 'center',
  },
  comingSoonCard: {
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardContent: {
    alignItems: 'center',
    padding: 24,
  },
  icon: {
    marginBottom: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    color: '#333',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  description: {
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  featuresList: {
    alignSelf: 'stretch',
    marginBottom: 32,
  },
  feature: {
    textAlign: 'center',
    marginBottom: 8,
    color: '#555',
  },
  notifyButton: {
    paddingVertical: 4,
    paddingHorizontal: 24,
  },
});