/**
 * Login Screen
 * Email-based authentication
 */

import React, { useState } from 'react';
import { View, StyleSheet, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { Card, TextInput, Button, Text, Divider } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

import { useAuth } from '../../contexts/AuthContext';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigation = useNavigation();

  const handleLogin = async () => {
    if (!email.trim()) {
      Alert.alert('Error', 'Please enter your email address');
      return;
    }

    try {
      setLoading(true);
      await login(email.trim().toLowerCase());
    } catch (error: any) {
      Alert.alert('Login Failed', error.message || 'Please try again');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = () => {
    navigation.navigate('Register' as never);
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        {/* Logo/Brand Section */}
        <View style={styles.brandSection}>
          <Text variant="displaySmall" style={styles.brandText}>
            ⚡ EV Platform
          </Text>
          <Text variant="bodyLarge" style={styles.tagline}>
            Sustainable mobility for everyone
          </Text>
        </View>

        {/* Login Form */}
        <Card style={styles.loginCard}>
          <Card.Content>
            <Text variant="headlineSmall" style={styles.loginTitle}>
              Welcome Back
            </Text>
            <Text variant="bodyMedium" style={styles.loginSubtitle}>
              Enter your email to continue
            </Text>

            <TextInput
              label="Email Address"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              style={styles.input}
            />

            <Button
              mode="contained"
              onPress={handleLogin}
              loading={loading}
              disabled={loading}
              style={styles.loginButton}
            >
              Continue
            </Button>

            <Divider style={styles.divider} />

            <Button
              mode="outlined"
              onPress={handleRegister}
              disabled={loading}
              style={styles.registerButton}
            >
              Create New Account
            </Button>
          </Card.Content>
        </Card>

        {/* Features Section */}
        <View style={styles.featuresSection}>
          <Text variant="bodySmall" style={styles.featuresText}>
            🚗 Book rides • 📦 Send parcels • 🔋 Rent EVs • 🎁 Earn rewards
          </Text>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  brandSection: {
    alignItems: 'center',
    marginBottom: 48,
  },
  brandText: {
    color: '#4CAF50',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  tagline: {
    color: '#666',
    textAlign: 'center',
  },
  loginCard: {
    elevation: 4,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  loginTitle: {
    textAlign: 'center',
    marginBottom: 8,
    color: '#333',
  },
  loginSubtitle: {
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  input: {
    marginBottom: 16,
  },
  loginButton: {
    marginBottom: 16,
    paddingVertical: 4,
  },
  divider: {
    marginVertical: 16,
  },
  registerButton: {
    paddingVertical: 4,
  },
  featuresSection: {
    marginTop: 32,
    alignItems: 'center',
  },
  featuresText: {
    color: '#999',
    textAlign: 'center',
    lineHeight: 20,
  },
});