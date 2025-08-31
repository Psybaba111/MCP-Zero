/**
 * API Context for Ops Dashboard
 * Handles API calls to backend services
 */

import React, { createContext, useContext, ReactNode } from 'react';
import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface ApiContextType {
  apiCall: (endpoint: string, method?: string, data?: any) => Promise<any>;
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
      const token = localStorage.getItem('ops_auth_token');
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response: AxiosResponse = await axios({
        method: method.toLowerCase(),
        url: `${API_BASE_URL}${endpoint}`,
        data,
        headers,
        timeout: 30000,
      });
      
      return response.data;
    } catch (error: any) {
      if (error.response) {
        const { status, data } = error.response;
        
        if (status === 401) {
          // Token expired - redirect to login
          localStorage.removeItem('ops_auth_token');
          localStorage.removeItem('ops_user_data');
          window.location.href = '/login';
        }
        
        throw new Error(data?.detail || `Request failed with status ${status}`);
      } else if (error.request) {
        throw new Error('Network error - please check your connection');
      } else {
        throw new Error(error.message || 'An unexpected error occurred');
      }
    }
  };

  const value: ApiContextType = {
    apiCall,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};