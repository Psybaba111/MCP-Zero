/**
 * Theme configuration for React Native Paper
 * Modern EV platform design system
 */

import { MD3LightTheme as DefaultTheme, configureFonts } from 'react-native-paper';

const fontConfig = {
  web: {
    regular: {
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: '400' as const,
    },
    medium: {
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: '500' as const,
    },
    light: {
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: '300' as const,
    },
    thin: {
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      fontWeight: '100' as const,
    },
  },
  ios: {
    regular: {
      fontFamily: 'System',
      fontWeight: '400' as const,
    },
    medium: {
      fontFamily: 'System',
      fontWeight: '500' as const,
    },
    light: {
      fontFamily: 'System',
      fontWeight: '300' as const,
    },
    thin: {
      fontFamily: 'System',
      fontWeight: '100' as const,
    },
  },
  android: {
    regular: {
      fontFamily: 'Roboto',
      fontWeight: '400' as const,
    },
    medium: {
      fontFamily: 'Roboto',
      fontWeight: '500' as const,
    },
    light: {
      fontFamily: 'Roboto',
      fontWeight: '300' as const,
    },
    thin: {
      fontFamily: 'Roboto',
      fontWeight: '100' as const,
    },
  },
};

export const theme = {
  ...DefaultTheme,
  fonts: configureFonts({ config: fontConfig }),
  colors: {
    ...DefaultTheme.colors,
    primary: '#4CAF50',
    primaryContainer: '#E8F5E8',
    secondary: '#2196F3',
    secondaryContainer: '#E3F2FD',
    tertiary: '#FF9800',
    tertiaryContainer: '#FFF3E0',
    surface: '#FFFFFF',
    surfaceVariant: '#F5F5F5',
    background: '#FAFAFA',
    error: '#F44336',
    errorContainer: '#FFEBEE',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onSurface: '#1C1B1F',
    onSurfaceVariant: '#49454F',
    outline: '#79747E',
    shadow: '#000000',
    scrim: '#000000',
  },
};