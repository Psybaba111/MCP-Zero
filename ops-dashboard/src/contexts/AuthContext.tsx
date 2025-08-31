/**
 * Authentication Context for Ops Dashboard
 * Manages admin user authentication
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored authentication
    const storedToken = localStorage.getItem('ops_auth_token');
    const storedUser = localStorage.getItem('ops_user_data');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // Mock login for ops dashboard
      // In production, this would call the actual backend API
      const mockUser = {
        id: '1',
        email: email,
        full_name: 'Operations Admin',
        role: 'admin'
      };
      
      const mockToken = 'mock-ops-token-' + Date.now();
      
      localStorage.setItem('ops_auth_token', mockToken);
      localStorage.setItem('ops_user_data', JSON.stringify(mockUser));
      
      setToken(mockToken);
      setUser(mockUser);
    } catch (error) {
      throw new Error('Invalid credentials');
    }
  };

  const logout = () => {
    localStorage.removeItem('ops_auth_token');
    localStorage.removeItem('ops_user_data');
    setToken(null);
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};