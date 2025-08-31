/**
 * API Context
 * Handles API calls with authentication and error handling
 */

import React, { createContext, useContext, ReactNode } from 'react';
import axios, { AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiContextType {
  apiCall: (endpoint: string, method: string, data?: any) => Promise<any>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

export const ApiProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const apiCall = async (endpoint: string, method: string = 'GET', data?: any): Promise<any> => {
    try {
      // Get stored token
      const token = await AsyncStorage.getItem('auth_token');
      
      // Configure headers
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Make API call
      const response: AxiosResponse = await axios({
        method: method.toLowerCase(),
        url: `${API_BASE_URL}${endpoint}`,
        data,
        headers,
        timeout: 30000,
      });
      
      return response.data;
    } catch (error: any) {
      // Handle different error types
      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;
        
        if (status === 401) {
          // Token expired or invalid - logout user
          await AsyncStorage.removeItem('auth_token');
          await AsyncStorage.removeItem('user_data');
          // Could trigger a logout event here
        }
        
        throw new Error(data?.detail || `Request failed with status ${status}`);
      } else if (error.request) {
        // Network error
        throw new Error('Network error - please check your connection');
      } else {
        // Other error
        throw new Error(error.message || 'An unexpected error occurred');
      }
    }
  };

  const value: ApiContextType = {
    apiCall,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};