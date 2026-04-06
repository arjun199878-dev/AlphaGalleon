import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider, DefaultTheme, Button, Text } from 'react-native-paper';
import { View } from 'react-native';

// Import Screens (Currently inline for quick test)
// In real structure, these will be separate files.

function BrainScreen({ navigation }) {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text variant="headlineMedium">🧠 The Brain</Text>
      <Text style={{ margin: 20 }}>Investment Memos & Live Analysis</Text>
      <Button mode="contained" onPress={() => alert('Brain Module Loading...')}>
        Generate Memo
      </Button>
    </View>
  );
}

function DoctorScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text variant="headlineMedium">🩺 The Doctor</Text>
      <Text style={{ margin: 20 }}>Portfolio Diagnosis</Text>
      <Button mode="contained" onPress={() => alert('Doctor Module Loading...')}>
        Check Portfolio
      </Button>
    </View>
  );
}

function ArchitectScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text variant="headlineMedium">🏗️ The Architect</Text>
      <Text style={{ margin: 20 }}>Wealth Planning</Text>
      <Button mode="contained" onPress={() => alert('Architect Module Loading...')}>
        Build Plan
      </Button>
    </View>
  );
}

const Tab = createBottomTabNavigator();

function MyTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Brain') {
            return <Text>🧠</Text>;
          } else if (route.name === 'Doctor') {
            return <Text>🩺</Text>;
          } else if (route.name === 'Architect') {
            return <Text>🏗️</Text>;
          }
        },
        tabBarActiveTintColor: 'tomato',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Brain" component={BrainScreen} />
      <Tab.Screen name="Doctor" component={DoctorScreen} />
      <Tab.Screen name="Architect" component={ArchitectScreen} />
    </Tab.Navigator>
  );
}

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#6200ee',
    accent: '#03dac4',
  },
};

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <MyTabs />
      </NavigationContainer>
    </PaperProvider>
  );
}
