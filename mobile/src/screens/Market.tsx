import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { getMarketQuote } from '../api/client';

const Market = () => {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [quote, setQuote] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchQuote = async () => {
    setLoading(true);
    setError('');
    const data = await getMarketQuote(symbol);
    if (data && data.data) {
      setQuote(data.data);
    } else {
      setError('Failed to fetch quote. Check symbol and try again.');
      setQuote(null);
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Market Data</Text>

      <View style={styles.searchRow}>
        <TextInput
          style={styles.input}
          value={symbol}
          onChangeText={setSymbol}
          placeholder="Enter Ticker (e.g. RELIANCE)"
          autoCapitalize="characters"
        />
        <TouchableOpacity style={styles.button} onPress={fetchQuote}>
          <Text style={styles.buttonText}>Search</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#4f46e5" style={{ marginTop: 20 }} />}

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      {quote && !loading && (
        <View style={styles.card}>
          <Text style={styles.symbolName}>{quote.instrument_token}</Text>
          <Text style={styles.price}>₹{quote.last_price || quote.ltp || 'N/A'}</Text>
          <Text style={styles.detail}>Close: ₹{quote.close_price}</Text>
          <Text style={styles.detail}>Volume: {quote.volume || 'N/A'}</Text>
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
  searchRow: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginRight: 12,
  },
  button: {
    backgroundColor: '#4f46e5',
    paddingHorizontal: 20,
    justifyContent: 'center',
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
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
    alignItems: 'center',
  },
  symbolName: {
    fontSize: 18,
    color: '#64748b',
    marginBottom: 8,
  },
  price: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 12,
  },
  detail: {
    fontSize: 16,
    color: '#475569',
    marginBottom: 4,
  },
  errorText: {
    color: '#ef4444',
    textAlign: 'center',
    marginTop: 10,
  },
});

export default Market;
