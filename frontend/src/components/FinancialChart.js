import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { BarChart } from 'react-native-chart-kit';
import theme from '../theme';

const FinancialChart = ({ data, title, type }) => {
  const screenWidth = Dimensions.get('window').width;

  const chartConfig = {
    backgroundColor: theme.colors.background,
    backgroundGradientFrom: theme.colors.background,
    backgroundGradientTo: theme.colors.background,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(19, 236, 91, ${opacity})`, // Neon Green
    labelColor: (opacity = 1) => `rgba(100, 116, 139, ${opacity})`, // Text Muted
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title} ({type})</Text>
      <BarChart
        data={data}
        width={screenWidth - 48}
        height={220}
        yAxisLabel="₹"
        yAxisSuffix="Cr"
        chartConfig={chartConfig}
        verticalLabelRotation={30}
        fromZero={true}
        showValuesOnTopOfBars={true}
        style={styles.chart}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 16,
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  title: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  chart: {
    borderRadius: 16,
  },
});

export default FinancialChart;
