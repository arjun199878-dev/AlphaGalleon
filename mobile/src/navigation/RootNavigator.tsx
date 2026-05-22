import React, { useContext } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import AppNavigator from './AppNavigator';
import AuthNavigator from './AuthNavigator';
import { AuthContext } from '../context/AuthContext';

const RootNavigator = () => {
  const { userToken, isInitializing } = useContext(AuthContext);

  if (isInitializing) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#4f46e5" />
      </View>
    );
  }

  return userToken ? <AppNavigator /> : <AuthNavigator />;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
});

export default RootNavigator;
