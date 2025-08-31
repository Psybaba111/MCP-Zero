/**
 * Registration Screen
 * User account creation with role selection
 */

import React, { useState } from 'react';
import { View, StyleSheet, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { Card, TextInput, Button, Text, SegmentedButtons } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

import { useAuth } from '../../contexts/AuthContext';

export default function RegisterScreen() {
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    full_name: '',
    role: 'passenger'
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigation = useNavigation();

  const handleRegister = async () => {
    // Validate form
    if (!formData.email.trim() || !formData.phone.trim() || !formData.full_name.trim()) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (!formData.email.includes('@')) {
      Alert.alert('Error', 'Please enter a valid email address');
      return;
    }

    try {
      setLoading(true);
      await register(formData);
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message || 'Please try again');
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.registerCard}>
          <Card.Content>
            <Text variant="headlineSmall" style={styles.title}>
              Create Account
            </Text>
            <Text variant="bodyMedium" style={styles.subtitle}>
              Join the sustainable mobility revolution
            </Text>

            <TextInput
              label="Full Name *"
              value={formData.full_name}
              onChangeText={(value) => updateFormData('full_name', value)}
              mode="outlined"
              style={styles.input}
            />

            <TextInput
              label="Email Address *"
              value={formData.email}
              onChangeText={(value) => updateFormData('email', value)}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              style={styles.input}
            />

            <TextInput
              label="Phone Number *"
              value={formData.phone}
              onChangeText={(value) => updateFormData('phone', value)}
              mode="outlined"
              keyboardType="phone-pad"
              autoComplete="tel"
              style={styles.input}
            />

            <Text variant="bodyMedium" style={styles.roleLabel}>
              I want to:
            </Text>
            <SegmentedButtons
              value={formData.role}
              onValueChange={(value) => updateFormData('role', value)}
              buttons={[
                { value: 'passenger', label: 'Book Rides' },
                { value: 'driver', label: 'Drive & Earn' },
                { value: 'owner', label: 'List My EV' },
              ]}
              style={styles.roleSelector}
            />

            <Button
              mode="contained"
              onPress={handleRegister}
              loading={loading}
              disabled={loading}
              style={styles.registerButton}
            >
              Create Account
            </Button>

            <Button
              mode="text"
              onPress={() => navigation.goBack()}
              disabled={loading}
              style={styles.backButton}
            >
              Already have an account? Sign In
            </Button>
          </Card.Content>
        </Card>

        <View style={styles.termsSection}>
          <Text variant="bodySmall" style={styles.termsText}>
            By creating an account, you agree to our Terms of Service and Privacy Policy
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
  },
  registerCard: {
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    color: '#333',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  input: {
    marginBottom: 16,
  },
  roleLabel: {
    marginBottom: 8,
    color: '#333',
  },
  roleSelector: {
    marginBottom: 24,
  },
  registerButton: {
    marginBottom: 16,
    paddingVertical: 4,
  },
  backButton: {
    paddingVertical: 4,
  },
  termsSection: {
    marginTop: 24,
    alignItems: 'center',
  },
  termsText: {
    color: '#999',
    textAlign: 'center',
    lineHeight: 18,
  },
});