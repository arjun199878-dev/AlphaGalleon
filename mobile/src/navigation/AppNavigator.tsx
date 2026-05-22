import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home as HomeIcon, FileText, Briefcase, TrendingUp, Settings as SettingsIcon } from 'lucide-react-native';

import Home from '../screens/Home';
import Memos from '../screens/Memos';
import Portfolio from '../screens/Portfolio';
import Market from '../screens/Market';
import Settings from '../screens/Settings';

const Tab = createBottomTabNavigator();

const AppNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#4f46e5',
        tabBarInactiveTintColor: '#94a3b8',
        headerShown: true,
        headerTitleAlign: 'center',
        headerStyle: { backgroundColor: '#f8fafc' },
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={Home}
        options={{
          tabBarIcon: ({ color, size }) => <HomeIcon color={color} size={size} />
        }}
      />
      <Tab.Screen
        name="Memos"
        component={Memos}
        options={{
          tabBarIcon: ({ color, size }) => <FileText color={color} size={size} />
        }}
      />
      <Tab.Screen
        name="Portfolio"
        component={Portfolio}
        options={{
          tabBarIcon: ({ color, size }) => <Briefcase color={color} size={size} />
        }}
      />
      <Tab.Screen
        name="Market"
        component={Market}
        options={{
          tabBarIcon: ({ color, size }) => <TrendingUp color={color} size={size} />
        }}
      />
      <Tab.Screen
        name="Settings"
        component={Settings}
        options={{
          tabBarIcon: ({ color, size }) => <SettingsIcon color={color} size={size} />,
          headerShown: false // Settings screen has its own custom header
        }}
      />
    </Tab.Navigator>
  );
};

export default AppNavigator;
