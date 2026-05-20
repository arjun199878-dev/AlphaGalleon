import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { constructPortfolio, getTaskStatus } from '../api/client';

const Portfolio = () => {
  const [capital, setCapital] = useState('100000');
  const [riskProfile, setRiskProfile] = useState('moderate');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleConstruct = async () => {
    setLoading(true);
    setResult(null);
    const response = await constructPortfolio({
      age: 30,
      risk_appetite: riskProfile,
      capital_amount: parseFloat(capital),
      investment_horizon: '5 years',
      goals: 'Wealth Building',
    });

    if (response && response.task_id) {
        pollTaskStatus(response.task_id);
    } else {
        setLoading(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const checkStatus = async () => {
        const taskData = await getTaskStatus(taskId);
        if (taskData) {
            if (taskData.status === "SUCCESS") {
                setResult(taskData.result);
                setLoading(false);
            } else if (taskData.status === "FAILURE") {
                console.error("Task failed:", taskData.error);
                setLoading(false);
            } else {
                // Pending/Processing, keep polling
                setTimeout(checkStatus, 2000);
            }
        } else {
            setLoading(false);
        }
    };
    checkStatus();
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Portfolio Builder</Text>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Capital Amount (₹)</Text>
        <TextInput
          style={styles.input}
          value={capital}
          onChangeText={setCapital}
          keyboardType="numeric"
        />
      </View>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Risk Profile</Text>
        <TextInput
          style={styles.input}
          value={riskProfile}
          onChangeText={setRiskProfile}
          autoCapitalize="none"
        />
      </View>

      <TouchableOpacity style={styles.button} onPress={handleConstruct} disabled={loading}>
        <Text style={styles.buttonText}>{loading ? 'Building...' : 'Construct Portfolio'}</Text>
      </TouchableOpacity>

      {loading && <ActivityIndicator size="large" color="#4f46e5" style={{ marginTop: 20 }} />}

      {result && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>Model Portfolio</Text>
          <Text style={styles.resultText}>Expected Return: {result.expected_return}%</Text>
          <Text style={styles.resultText}>Risk Level: {result.risk_level}</Text>
          <Text style={styles.allocationTitle}>Allocations:</Text>
          {result.allocations?.map((item: any, index: number) => (
            <Text key={index} style={styles.resultText}>
              • {item.ticker}: {item.percentage}% ({item.shares} shares)
            </Text>
          ))}
        </View>
      )}
    </ScrollView>
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
  formGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  button: {
    backgroundColor: '#4f46e5',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginTop: 24,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 2,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#1e293b',
  },
  resultText: {
    fontSize: 14,
    color: '#334155',
    marginBottom: 6,
  },
  allocationTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 12,
    marginBottom: 8,
    color: '#0f172a',
  },
});

export default Portfolio;
