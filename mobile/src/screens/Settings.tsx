import React, { useContext, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { Settings as SettingsIcon, Link2, User } from 'lucide-react-native';

const Settings = () => {
  const { logout, userInfo } = useContext(AuthContext);
  const [preferredBroker, setPreferredBroker] = useState(userInfo?.preferred_broker || 'upstox');

  const handleLinkBroker = (brokerId: string) => {
    // In a real app this would initiate the OAuth flow, likely via expo-web-browser
    Alert.alert('Link Broker', `Initiating OAuth flow for ${brokerId.toUpperCase()}...`);
    setPreferredBroker(brokerId);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <SettingsIcon size={32} color="#0f172a" />
        <Text style={styles.title}>Settings</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account Profile</Text>
        <View style={styles.card}>
          <View style={styles.row}>
            <User size={20} color="#64748b" />
            <View style={styles.rowText}>
              <Text style={styles.label}>Name</Text>
              <Text style={styles.value}>{userInfo?.name || 'Unknown User'}</Text>
            </View>
          </View>
          <View style={[styles.row, { borderTopWidth: 1, borderTopColor: '#f1f5f9', paddingTop: 16 }]}>
            <Text style={styles.label}>Email</Text>
            <Text style={styles.value}>{userInfo?.email || 'N/A'}</Text>
          </View>
          <View style={[styles.row, { borderTopWidth: 1, borderTopColor: '#f1f5f9', paddingTop: 16 }]}>
            <Text style={styles.label}>Risk Profile</Text>
            <Text style={[styles.value, { textTransform: 'capitalize' }]}>{userInfo?.riskProfile || 'Moderate'}</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Broker Integrations</Text>
        <Text style={styles.sectionDesc}>Connect your Demat accounts to allow AlphaGalleon to analyze holdings and execute AI-generated baskets.</Text>

        <View style={styles.card}>
          <TouchableOpacity
            style={[styles.brokerButton, preferredBroker === 'upstox' && styles.brokerActive]}
            onPress={() => handleLinkBroker('upstox')}
          >
            <View style={styles.brokerLeft}>
              <Text style={styles.brokerName}>Upstox</Text>
              {preferredBroker === 'upstox' && <Text style={styles.activeTag}>Preferred</Text>}
            </View>
            <Link2 size={20} color={preferredBroker === 'upstox' ? '#4f46e5' : '#94a3b8'} />
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.brokerButton, preferredBroker === 'zerodha' && styles.brokerActive]}
            onPress={() => handleLinkBroker('zerodha')}
          >
            <View style={styles.brokerLeft}>
              <Text style={styles.brokerName}>Zerodha (Kite)</Text>
              {preferredBroker === 'zerodha' && <Text style={styles.activeTag}>Preferred</Text>}
            </View>
            <Link2 size={20} color={preferredBroker === 'zerodha' ? '#4f46e5' : '#94a3b8'} />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.section}>
        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutText}>Sign Out of AlphaGalleon</Text>
        </TouchableOpacity>
      </View>

    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 24,
    paddingTop: 48,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  section: {
    paddingHorizontal: 24,
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#334155',
    marginBottom: 8,
  },
  sectionDesc: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 16,
    lineHeight: 20,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
    elevation: 2,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    marginBottom: 16,
  },
  rowText: {
    flex: 1,
  },
  label: {
    fontSize: 12,
    color: '#94a3b8',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  value: {
    fontSize: 16,
    color: '#0f172a',
    fontWeight: '500',
    marginTop: 4,
  },
  brokerButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginBottom: 12,
  },
  brokerActive: {
    borderColor: '#4f46e5',
    backgroundColor: '#e0e7ff',
  },
  brokerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  brokerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
  },
  activeTag: {
    fontSize: 10,
    fontWeight: 'bold',
    backgroundColor: '#4f46e5',
    color: '#fff',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    textTransform: 'uppercase',
  },
  logoutButton: {
    backgroundColor: '#fee2e2',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  logoutText: {
    color: '#ef4444',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default Settings;
