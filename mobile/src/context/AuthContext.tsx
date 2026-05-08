import React, { createContext, useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from '../api/client';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext<any>(null);

export const AuthProvider = ({ children }: any) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [userToken, setUserToken] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      setUserToken(null);
      setUserInfo(null);
      await AsyncStorage.removeItem('userToken');
      await AsyncStorage.removeItem('userInfo');
    } catch (e) {
      console.log('Logout error:', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const checkToken = useCallback(async () => {
    try {
      let token = await AsyncStorage.getItem('userToken');
      if (token) {
        // Here you could also decode the token to check expiry, or call /api/v1/auth/verify
        const decoded: any = jwtDecode(token);
        if (decoded.exp * 1000 < Date.now()) {
          // Token expired
          console.log('Token expired');
          await logout();
        } else {
          setUserToken(token);

          // Optionally fetch full user profile if needed
          const storedUser = await AsyncStorage.getItem('userInfo');
          if (storedUser) {
            setUserInfo(JSON.parse(storedUser));
          }
        }
      }
    } catch (e) {
      console.log('Error restoring token:', e);
    } finally {
      setIsInitializing(false);
    }
  }, [logout]);

  useEffect(() => {
    checkToken();
  }, [checkToken]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.post('/api/v1/auth/login', { email, password });

      if (response.data && response.data.token) {
        const { token, user } = response.data;
        setUserToken(token);
        setUserInfo(user);

        await AsyncStorage.setItem('userToken', token);
        await AsyncStorage.setItem('userInfo', JSON.stringify(user));
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed. Please check your credentials.');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (name: string, email: string, password: string, riskProfile: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.post('/api/v1/auth/signup', {
        name,
        email,
        password,
        riskProfile
      });

      if (response.data && response.data.token) {
        const { token, user } = response.data;
        setUserToken(token);
        setUserInfo(user);

        await AsyncStorage.setItem('userToken', token);
        await AsyncStorage.setItem('userInfo', JSON.stringify(user));
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Signup failed. Please try again.');
      console.error('Signup error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{
      login,
      signup,
      logout,
      isLoading,
      isInitializing,
      userToken,
      userInfo,
      error
    }}>
      {children}
    </AuthContext.Provider>
  );
};
