import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Change this to your computer's local IP address when running on a physical device,
// or use http://10.0.2.2:8000 for Android emulator and http://localhost:8000 for iOS simulator/web.
const API_BASE = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to attach the JWT token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('userToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const getSystemHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error fetching system health:', error);
    return null;
  }
};

export const getRecentMemos = async () => {
  try {
    const response = await apiClient.get('/api/v1/brain/memos');
    return response.data;
  } catch (error) {
    console.error('Error fetching recent memos:', error);
    return null;
  }
};

export const generateMemo = async (data: any) => {
  try {
    const response = await apiClient.post('/api/v1/brain/memo', data);
    return response.data;
  } catch (error) {
    console.error('Error generating memo:', error);
    return null;
  }
};

export const constructPortfolio = async (data: any) => {
  try {
    const response = await apiClient.post('/api/v1/architect/construct', data);
    return response.data;
  } catch (error) {
    console.error('Error constructing portfolio:', error);
    return null;
  }
};

export const getMarketQuote = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/api/v1/scout/quote/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching market quote:', error);
    return null;
  }
};

export default apiClient;

export const getTaskStatus = async (taskId: string) => {
  try {
    const response = await apiClient.get(`/api/v1/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching task status:', error);
    return null;
  }
};
