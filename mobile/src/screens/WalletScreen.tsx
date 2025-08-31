/**
 * Wallet Screen
 * Payment history, points balance, and redemptions
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, Alert } from 'react-native';
import { Card, Text, Button, Divider, ActivityIndicator, Chip } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';

import { useApi } from '../contexts/ApiContext';
import { useAuth } from '../contexts/AuthContext';

export default function WalletScreen() {
  const [rewardAccount, setRewardAccount] = useState<any>(null);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [rewardEvents, setRewardEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('balance');
  const { apiCall } = useApi();
  const { user } = useAuth();

  useEffect(() => {
    loadWalletData();
  }, []);

  const loadWalletData = async () => {
    try {
      setLoading(true);
      
      const [rewardResponse, paymentsResponse, eventsResponse] = await Promise.all([
        apiCall('/rewards/balance'),
        apiCall('/payments'),
        apiCall('/rewards/events')
      ]);
      
      setRewardAccount(rewardResponse);
      setPaymentHistory(paymentsResponse);
      setRewardEvents(eventsResponse);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load wallet data');
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier: string) => {
    const colors = {
      bronze: '#CD7F32',
      silver: '#C0C0C0',
      gold: '#FFD700',
      platinum: '#E5E4E2'
    };
    return colors[tier as keyof typeof colors] || '#CD7F32';
  };

  const getTierIcon = (tier: string) => {
    const icons = {
      bronze: 'medal',
      silver: 'medal',
      gold: 'medal',
      platinum: 'crown'
    };
    return icons[tier as keyof typeof icons] || 'medal';
  };

  const renderPaymentItem = ({ item: payment }: { item: any }) => (
    <Card style={styles.historyCard}>
      <Card.Content>
        <View style={styles.historyHeader}>
          <Text variant="titleMedium">
            {payment.entity_type.charAt(0).toUpperCase() + payment.entity_type.slice(1)}
          </Text>
          <Text variant="titleMedium" style={styles.amount}>
            ₹{payment.amount}
          </Text>
        </View>
        
        <View style={styles.historyDetails}>
          <Chip 
            compact 
            style={[styles.statusChip, { backgroundColor: getStatusColor(payment.status) }]}
          >
            {payment.status}
          </Chip>
          <Text variant="bodySmall" style={styles.date}>
            {new Date(payment.created_at).toLocaleDateString()}
          </Text>
        </View>
      </Card.Content>
    </Card>
  );

  const renderRewardEvent = ({ item: event }: { item: any }) => (
    <Card style={styles.historyCard}>
      <Card.Content>
        <View style={styles.historyHeader}>
          <Text variant="titleMedium">
            {event.event_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
          </Text>
          <Text variant="titleMedium" style={styles.pointsEarned}>
            +{event.points_earned} pts
          </Text>
        </View>
        
        <Text variant="bodySmall" style={styles.date}>
          {new Date(event.created_at).toLocaleDateString()}
        </Text>
      </Card.Content>
    </Card>
  );

  const getStatusColor = (status: string) => {
    const colors = {
      completed: '#4CAF50',
      pending: '#FF9800',
      failed: '#F44336',
      processing: '#2196F3'
    };
    return colors[status as keyof typeof colors] || '#999';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Loading wallet...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Rewards Balance Card */}
      <Card style={styles.balanceCard}>
        <Card.Content>
          <View style={styles.balanceHeader}>
            <View>
              <Text variant="bodyLarge" style={styles.balanceLabel}>
                Reward Points
              </Text>
              <Text variant="displaySmall" style={styles.balance}>
                {rewardAccount?.points_balance || 0}
              </Text>
            </View>
            
            <View style={styles.tierBadge}>
              <MaterialCommunityIcons 
                name={getTierIcon(rewardAccount?.tier || 'bronze')} 
                size={24} 
                color={getTierColor(rewardAccount?.tier || 'bronze')}
              />
              <Text variant="labelLarge" style={[styles.tierText, { color: getTierColor(rewardAccount?.tier || 'bronze') }]}>
                {(rewardAccount?.tier || 'bronze').toUpperCase()}
              </Text>
            </View>
          </View>
          
          <Button 
            mode="contained-tonal" 
            style={styles.redeemButton}
            icon="gift"
          >
            Redeem Points
          </Button>
        </Card.Content>
      </Card>

      {/* Tab Selector */}
      <View style={styles.tabContainer}>
        <Button
          mode={activeTab === 'balance' ? 'contained' : 'outlined'}
          onPress={() => setActiveTab('balance')}
          style={styles.tabButton}
        >
          Balance
        </Button>
        <Button
          mode={activeTab === 'payments' ? 'contained' : 'outlined'}
          onPress={() => setActiveTab('payments')}
          style={styles.tabButton}
        >
          Payments
        </Button>
        <Button
          mode={activeTab === 'rewards' ? 'contained' : 'outlined'}
          onPress={() => setActiveTab('rewards')}
          style={styles.tabButton}
        >
          Rewards
        </Button>
      </View>

      {/* Content */}
      {activeTab === 'payments' && (
        <FlatList
          data={paymentHistory}
          keyExtractor={(item: any) => item.id}
          renderItem={renderPaymentItem}
          contentContainerStyle={styles.historyList}
          showsVerticalScrollIndicator={false}
          onRefresh={loadWalletData}
          refreshing={loading}
        />
      )}

      {activeTab === 'rewards' && (
        <FlatList
          data={rewardEvents}
          keyExtractor={(item: any) => item.id}
          renderItem={renderRewardEvent}
          contentContainerStyle={styles.historyList}
          showsVerticalScrollIndicator={false}
          onRefresh={loadWalletData}
          refreshing={loading}
        />
      )}

      {activeTab === 'balance' && (
        <View style={styles.balanceContent}>
          <Card style={styles.infoCard}>
            <Card.Content>
              <Text variant="titleMedium" style={styles.infoTitle}>
                How to Earn Points
              </Text>
              <Text variant="bodyMedium" style={styles.infoText}>
                • Complete rides: 10 points{'\n'}
                • Return rentals on time: 25 points{'\n'}
                • Complete KYC: 100 points{'\n'}
                • Refer friends: 200 points
              </Text>
            </Card.Content>
          </Card>
        </View>
      )}
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
  balanceCard: {
    margin: 16,
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  balanceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  balanceLabel: {
    color: '#666',
  },
  balance: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  tierBadge: {
    alignItems: 'center',
    gap: 4,
  },
  tierText: {
    fontWeight: 'bold',
    fontSize: 12,
  },
  redeemButton: {
    marginTop: 8,
  },
  tabContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  tabButton: {
    flex: 1,
  },
  historyList: {
    padding: 16,
    gap: 12,
  },
  historyCard: {
    elevation: 2,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  amount: {
    color: '#333',
    fontWeight: 'bold',
  },
  pointsEarned: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  historyDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusChip: {
    height: 24,
  },
  date: {
    color: '#666',
  },
  balanceContent: {
    padding: 16,
  },
  infoCard: {
    elevation: 2,
  },
  infoTitle: {
    marginBottom: 12,
    color: '#333',
  },
  infoText: {
    color: '#666',
    lineHeight: 20,
  },
});