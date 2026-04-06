import "expo-standard-web-crypto";
import React, { Component } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

// Auth
import { AuthProvider, useAuth } from './src/context/AuthContext';
import { COLORS } from './src/theme';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import MemoScreen from './src/screens/MemoScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';
import DoctorScreen from './src/screens/DoctorScreen';
import BacktestScreen from './src/screens/BacktestScreen';
import ToolsScreen from './src/screens/ToolsScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const convex = new ConvexReactClient("https://vibrant-spoonbill-564.eu-west-1.convex.cloud", {
  unsavedChangesWarning: false,
});

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// ── Error Boundary ─────────────────────────────────────────────────────────
class CockpitErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>SYSTEM_CRITICAL_FAILURE</Text>
          <Text style={styles.errorText}>{this.state.error?.toString()}</Text>
        </View>
      );
    }
    return this.props.children;
  }
}

// ── Home Stack (Home → Memo) ───────────────────────────────────────────────
function HomeStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: COLORS.background },
        headerTintColor: COLORS.primary,
        headerTitleStyle: { fontWeight: 'bold', color: COLORS.text },
      }}
    >
      <Stack.Screen name="HomeMain" component={HomeScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Memo" component={MemoScreen} options={({ route }) => ({ title: route.params?.symbol || 'Memo' })} />
    </Stack.Navigator>
  );
}

// ── Tools Stack (Tools → Portfolio / Doctor / Backtest) ────────────────────
function ToolsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: COLORS.background },
        headerTintColor: COLORS.primary,
        headerTitleStyle: { fontWeight: 'bold', color: COLORS.text },
      }}
    >
      <Stack.Screen name="ToolsMain" component={ToolsScreen} options={{ title: 'Tools' }} />
      <Stack.Screen name="Portfolio" component={PortfolioScreen} options={{ title: 'Portfolio Architect' }} />
      <Stack.Screen name="Doctor" component={DoctorScreen} options={{ title: 'Portfolio Doctor' }} />
      <Stack.Screen name="Backtest" component={BacktestScreen} options={{ title: 'Time Travel' }} />
    </Stack.Navigator>
  );
}

// ── Bottom Tab Navigator (main app shell) ──────────────────────────────────
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: COLORS.surface,
          borderTopColor: COLORS.border,
          borderTopWidth: 1,
          paddingBottom: 6,
          paddingTop: 6,
          height: 60,
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textMuted,
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Home') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'Tools') iconName = focused ? 'grid' : 'grid-outline';
          else if (route.name === 'Profile') iconName = focused ? 'person' : 'person-outline';
          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeStack} />
      <Tab.Screen name="Tools" component={ToolsStack} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ headerShown: false }} />
    </Tab.Navigator>
  );
}

// ── Root Navigator — gates on auth ─────────────────────────────────────────
function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false, animation: 'fade' }}>
      {user ? (
        <Stack.Screen name="Main" component={MainTabs} />
      ) : (
        <Stack.Screen name="Login" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
}

// ── App Root ───────────────────────────────────────────────────────────────
export default function App() {
  return (
    <CockpitErrorBoundary>
      <ConvexProvider client={convex}>
        <AuthProvider convexClient={convex}>
          <NavigationContainer>
            <RootNavigator />
          </NavigationContainer>
        </AuthProvider>
      </ConvexProvider>
    </CockpitErrorBoundary>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    backgroundColor: '#050505',
    justifyContent: 'center',
    padding: 40,
  },
  errorTitle: {
    color: '#ef4444',
    fontSize: 24,
    fontWeight: 'bold',
    fontFamily: 'monospace',
    marginBottom: 20,
  },
  errorText: {
    color: '#E2E8F0',
    fontSize: 14,
    fontFamily: 'monospace',
    lineHeight: 20,
  },
});
