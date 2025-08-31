/**
 * Payment Sheet
 * Hyperswitch payment integration
 */

import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Card, Text, Button, ActivityIndicator, Divider } from 'react-native-paper';
import { useRoute, useNavigation } from '@react-navigation/native';

import { useApi } from '../../contexts/ApiContext';
import { useAuth } from '../../contexts/AuthContext';

export default function PaymentSheet() {
  const [loading, setLoading] = useState(false);
  const [paymentProcessing, setPaymentProcessing] = useState(false);
  const route = useRoute();
  const navigation = useNavigation();
  const { apiCall } = useApi();
  const { user } = useAuth();
  
  const { bookingData, entityType } = route.params as any;

  const handlePayment = async () => {
    try {
      setLoading(true);
      
      // Create ride/parcel first
      let entityResponse;
      if (entityType === 'ride') {
        entityResponse = await apiCall('/rides', 'POST', bookingData);
      } else if (entityType === 'parcel') {
        entityResponse = await apiCall('/parcels', 'POST', bookingData);
      } else if (entityType === 'rental') {
        entityResponse = await apiCall('/rentals', 'POST', bookingData);
      }
      
      // Create payment intent
      const paymentIntent = await apiCall('/payments/intents', 'POST', {
        entity_type: entityType,
        entity_id: entityResponse.id,
        amount: bookingData.estimated_fare || bookingData.total_amount
      });
      
      setPaymentProcessing(true);
      
      // Simulate payment processing (in real app, use Stripe/Hyperswitch SDK)
      setTimeout(async () => {
        try {
          // Mock successful payment
          await simulatePaymentSuccess(paymentIntent.payment_intent_id, entityResponse.id);
          
          navigation.navigate('BookingConfirmation' as never, { 
            entityType,
            entityId: entityResponse.id,
            paymentIntentId: paymentIntent.payment_intent_id
          } as never);
        } catch (error: any) {
          Alert.alert('Payment Failed', error.message || 'Please try again');
        } finally {
          setPaymentProcessing(false);
        }
      }, 2000);
      
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  const simulatePaymentSuccess = async (paymentIntentId: string, entityId: string) => {
    // Simulate webhook call to update payment status
    await apiCall('/payments/webhooks', 'POST', {
      event_type: 'payment_intent.succeeded',
      payment_intent_id: paymentIntentId,
      status: 'succeeded',
      amount: (bookingData.estimated_fare || bookingData.total_amount) * 100,
      currency: 'INR'
    });
  };

  const getEntityTitle = () => {
    switch (entityType) {
      case 'ride': return 'Book Ride';
      case 'parcel': return 'Send Parcel';
      case 'rental': return 'Rent Vehicle';
      default: return 'Payment';
    }
  };

  return (
    <View style={styles.container}>
      <Card style={styles.paymentCard}>
        <Card.Content>
          <Text variant="headlineSmall" style={styles.title}>
            {getEntityTitle()}
          </Text>
          
          <Divider style={styles.divider} />
          
          {/* Booking Summary */}
          <View style={styles.summarySection}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Booking Summary
            </Text>
            
            {entityType === 'ride' && (
              <>
                <View style={styles.summaryRow}>
                  <Text variant="bodyMedium">From:</Text>
                  <Text variant="bodyMedium" style={styles.summaryValue}>
                    {bookingData.pickup_address}
                  </Text>
                </View>
                <View style={styles.summaryRow}>
                  <Text variant="bodyMedium">To:</Text>
                  <Text variant="bodyMedium" style={styles.summaryValue}>
                    {bookingData.drop_address}
                  </Text>
                </View>
                <View style={styles.summaryRow}>
                  <Text variant="bodyMedium">Vehicle:</Text>
                  <Text variant="bodyMedium" style={styles.summaryValue}>
                    {bookingData.vehicle_type}
                  </Text>
                </View>
              </>
            )}
            
            <View style={styles.summaryRow}>
              <Text variant="titleMedium">Total Amount:</Text>
              <Text variant="titleLarge" style={styles.totalAmount}>
                ₹{bookingData.estimated_fare || bookingData.total_amount}
              </Text>
            </View>
          </View>
          
          <Divider style={styles.divider} />
          
          {/* Payment Method */}
          <View style={styles.paymentSection}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Payment Method
            </Text>
            
            <Card style={styles.paymentMethodCard}>
              <Card.Content style={styles.paymentMethod}>
                <MaterialCommunityIcons name="credit-card" size={24} color="#4CAF50" />
                <Text variant="bodyMedium">UPI / Cards / Net Banking</Text>
              </Card.Content>
            </Card>
          </View>
          
          {paymentProcessing ? (
            <View style={styles.processingContainer}>
              <ActivityIndicator size="large" color="#4CAF50" />
              <Text variant="bodyLarge" style={styles.processingText}>
                Processing Payment...
              </Text>
            </View>
          ) : (
            <Button
              mode="contained"
              onPress={handlePayment}
              loading={loading}
              disabled={loading}
              style={styles.payButton}
            >
              Pay ₹{bookingData.estimated_fare || bookingData.total_amount}
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
    justifyContent: 'center',
    padding: 16,
  },
  paymentCard: {
    elevation: 8,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  title: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#333',
  },
  divider: {
    marginVertical: 16,
  },
  summarySection: {
    marginBottom: 16,
  },
  sectionTitle: {
    marginBottom: 12,
    color: '#333',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryValue: {
    flex: 1,
    textAlign: 'right',
    color: '#666',
  },
  totalAmount: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  paymentSection: {
    marginBottom: 24,
  },
  paymentMethodCard: {
    elevation: 1,
  },
  paymentMethod: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  processingContainer: {
    alignItems: 'center',
    padding: 24,
  },
  processingText: {
    marginTop: 16,
    color: '#666',
  },
  payButton: {
    paddingVertical: 8,
  },
});