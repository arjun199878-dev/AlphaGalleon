import React, { useEffect, useState, useContext } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { getSystemHealth } from '../api/client';
import { AuthContext } from '../context/AuthContext';

const Home = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { userInfo } = useContext(AuthContext);

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
      <View style={styles.headerRow}>
        <Text style={styles.title}>AlphaGalleon HQ</Text>
      </View>

      {userInfo && (
        <Text style={styles.welcomeText}>Welcome back, {userInfo.name || userInfo.email}</Text>
      )}

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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  welcomeText: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 20,
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
