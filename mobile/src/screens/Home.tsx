import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { getSystemHealth } from '../api/client';

const Home = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    const data = await getSystemHealth();
    setHealth(data);
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AlphaGalleon HQ</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#4f46e5" />
      ) : (
        <View style={styles.card}>
          <Text style={styles.text}>System Status: {health?.status || 'Offline'}</Text>
          <Text style={styles.text}>Environment: {health?.environment || 'Unknown'}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8fafc',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#0f172a',
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 2,
  },
  text: {
    fontSize: 16,
    color: '#334155',
    marginBottom: 8,
  },
});

export default Home;
