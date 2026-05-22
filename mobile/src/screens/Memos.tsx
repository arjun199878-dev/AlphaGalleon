import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator } from 'react-native';
import { getRecentMemos } from '../api/client';

const Memos = () => {
  const [memos, setMemos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMemos();
  }, []);

  const fetchMemos = async () => {
    const data = await getRecentMemos();
    // Assuming the API returns a list or an object with a 'memos' array.
    if (data && Array.isArray(data)) {
      setMemos(data);
    } else if (data && data.memos) {
      setMemos(data.memos);
    }
    setLoading(false);
  };

  const renderMemo = ({ item }: { item: any }) => (
    <View style={styles.card}>
      <Text style={styles.symbol}>{item.symbol || item.ticker_symbol || 'Unknown'}</Text>
      <Text style={[styles.verdict, item.verdict === 'BUY' ? styles.buy : styles.sell]}>
        {item.verdict || item.recommendation}
      </Text>
      <Text style={styles.summary} numberOfLines={3}>
        {item.summary || item.thesis_summary}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Recent Memos</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#4f46e5" />
      ) : memos.length === 0 ? (
        <Text style={styles.emptyText}>No memos found.</Text>
      ) : (
        <FlatList
          data={memos}
          keyExtractor={(item, index) => item._id || index.toString()}
          renderItem={renderMemo}
        />
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
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 2,
  },
  symbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  verdict: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 4,
    marginBottom: 8,
  },
  buy: {
    color: '#16a34a',
  },
  sell: {
    color: '#dc2626',
  },
  summary: {
    fontSize: 14,
    color: '#475569',
  },
  emptyText: {
    textAlign: 'center',
    color: '#94a3b8',
    marginTop: 20,
  },
});

export default Memos;
