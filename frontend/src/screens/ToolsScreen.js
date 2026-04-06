import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import theme, { COLORS, SPACING } from '../theme';
import { Ionicons } from '@expo/vector-icons';

const ToolsScreen = ({ navigation }) => {
  const tools = [
    { name: 'Portfolio Architect', icon: 'color-palette-outline', color: '#3B82F6', screen: 'Portfolio' },
    { name: 'Portfolio Doctor', icon: 'medkit-outline', color: '#10B981', screen: 'Doctor' },
    { name: 'Backtest (Time Travel)', icon: 'time-outline', color: '#8B5CF6', screen: 'Backtest' },
    { name: 'Tax Calculator', icon: 'calculator-outline', color: '#F59E0B', screen: null },
  ];

  const handleToolPress = (tool) => {
    if (tool.screen) {
      navigation.navigate(tool.screen);
    } else {
      Alert.alert('Coming Soon', `${tool.name} is under construction.`);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Products & Tools</Text>
        {tools.map((tool, index) => (
          <TouchableOpacity key={index} style={styles.toolCard} onPress={() => handleToolPress(tool)}>
            <View style={[styles.iconContainer, { backgroundColor: tool.color + '20' }]}>
              <Ionicons name={tool.icon} size={28} color={tool.color} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.toolName}>{tool.name}</Text>
              <Text style={styles.toolDesc}>Professional grade analysis at your fingertips.</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.textMuted} />
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  content: { padding: SPACING.l },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: SPACING.l, color: COLORS.text },
  toolCard: {
    backgroundColor: COLORS.surface,
    borderRadius: theme.borderRadius.m,
    padding: SPACING.m,
    marginBottom: SPACING.m,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  iconContainer: { width: 56, height: 56, borderRadius: theme.borderRadius.m, justifyContent: 'center', alignItems: 'center', marginRight: SPACING.m },
  textContainer: { flex: 1 },
  toolName: { fontSize: 16, fontWeight: 'bold', color: COLORS.text, marginBottom: 2 },
  toolDesc: { fontSize: 12, color: COLORS.textMuted },
});

export default ToolsScreen;
