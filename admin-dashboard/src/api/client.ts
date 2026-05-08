// API client for admin dashboard backend calls
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface APIResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface User {
  _id?: string;
  name: string;
  email: string;
  riskProfile?: 'conservative' | 'moderate' | 'aggressive' | 'No Profile';
  createdAt?: number;
}

export interface Activity {
  _id?: string;
  userId?: string;
  action: string;
  details: string;
  timestamp: number;
}

export interface Portfolio {
  _id: string;
  userId: string;
  name: string;
  capital: number;
  riskProfile: string;
  timeHorizon: string;
  status: 'active' | 'archived';
  createdAt: number;
  updatedAt: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
  expiresIn: number;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
  riskProfile?: string;
}

// User endpoints
export const listUsers = async (_limit: number = 100): Promise<User[]> => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/admin/users`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
      }
    });
    if (!response.ok) throw new Error('Failed to fetch users');
    return await response.json();
  } catch (error) {
    console.error('Error listing users:', error);
    return [];
  }
};

// Activity endpoints
export const listActivity = async (limit: number = 100): Promise<Activity[]> => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/admin/activity?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
      }
    });
    if (!response.ok) throw new Error('Failed to fetch activity');
    return await response.json();
  } catch (error) {
    console.error('Error listing activity:', error);
    return [];
  }
};

// Auth endpoints
export const login = async (email: string, password: string): Promise<LoginResponse | null> => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) throw new Error('Login failed');
    const data = await response.json();
    // Store token for future requests
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  } catch (error) {
    console.error('Error logging in:', error);
    return null;
  }
};

export const signup = async (name: string, email: string, password: string, riskProfile?: string): Promise<LoginResponse | null> => {
  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, riskProfile })
    });
    if (!response.ok) throw new Error('Signup failed');
    const data = await response.json();
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    return data;
  } catch (error) {
    console.error('Error signing up:', error);
    return null;
  }
};

export const logout = () => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const getCurrentUser = (): User | null => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};
