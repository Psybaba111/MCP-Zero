/**
 * EV Platform Mobile App
 * React Native app for ride-hailing, P2P EV rentals, and parcel delivery
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';

import { AuthProvider } from './src/contexts/AuthContext';
import { ApiProvider } from './src/contexts/ApiContext';
import RootNavigator from './src/navigation/RootNavigator';
import { theme } from './src/theme/theme';

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <AuthProvider>
        <ApiProvider>
          <NavigationContainer>
            <RootNavigator />
          </NavigationContainer>
          <StatusBar style="auto" />
        </ApiProvider>
      </AuthProvider>
    </PaperProvider>
  );
}