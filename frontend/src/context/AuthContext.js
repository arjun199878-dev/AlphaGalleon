import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const AuthContext = createContext(null);

const STORAGE_KEY = 'alphagalleon_user';

export const AuthProvider = ({ children, convexClient }) => {
    const [user, setUser] = useState(null); // { userId, name, email }
    const [loading, setLoading] = useState(true);

    // On mount, check if a user session already exists locally
    useEffect(() => {
        const loadUser = async () => {
            try {
                const stored = await AsyncStorage.getItem(STORAGE_KEY);
                if (stored) {
                    setUser(JSON.parse(stored));
                }
            } catch (e) {
                console.error('Failed to load user from storage:', e);
            } finally {
                setLoading(false);
            }
        };
        loadUser();
    }, []);

    /**
     * Called from LoginScreen after user enters name + email.
     * Creates the user record in Convex, then persists locally.
     */
    const login = async (name, email) => {
        try {
            // Create or retrieve user in Convex
            const userId = await convexClient.mutation('users:create', {
                name,
                email,
            });

            const userData = { userId: userId.toString(), name, email };
            await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
            setUser(userData);
        } catch (e) {
            console.error('Login error:', e);
            // Even if Convex fails, let user in with a local-only session
            const userData = { userId: null, name, email };
            await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
            setUser(userData);
        }
    };

    const logout = async () => {
        await AsyncStorage.removeItem(STORAGE_KEY);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
    return ctx;
};

export default AuthContext;
