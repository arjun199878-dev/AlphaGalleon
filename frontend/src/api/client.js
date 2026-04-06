import axios from 'axios';
import { Platform } from 'react-native';

// For Android Emulator use 10.0.2.2, for iOS Simulator use localhost
const BASE_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8001' : 'http://localhost:8001';

const client = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getMarketPrice = async (symbol) => {
    try {
        const response = await client.get(`/api/v1/market/price/${symbol}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching market price:', error);
        throw error;
    }
};

export const getInvestmentMemo = async (symbol) => {
    try {
        const response = await client.post('/api/v1/brain/memo', { symbol });
        return response.data;
    } catch (error) {
        console.error('Error generating memo:', error);
        throw error;
    }
};

export const generatePortfolio = async (capital, risk_profile, time_horizon) => {
    try {
        const response = await client.post('/api/v1/brain/portfolio', { 
            capital, risk_profile, time_horizon 
        });
        return response.data;
    } catch (error) {
        console.error('Error generating portfolio:', error);
        throw error;
    }
};

export const diagnosePortfolio = async (holdings) => {
    try {
        const response = await client.post('/api/v1/brain/diagnose', { holdings });
        return response.data;
    } catch (error) {
        console.error('Error diagnosing portfolio:', error);
        throw error;
    }
};

export const runBacktest = async (holdings, duration_years) => {
    try {
        const response = await client.post('/api/v1/brain/backtest', { holdings, duration_years });
        return response.data;
    } catch (error) {
        console.error('Error running backtest:', error);
        throw error;
    }
};

export default client;
