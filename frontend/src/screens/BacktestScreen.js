import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, ActivityIndicator, Alert, Dimensions } from 'react-native';
import theme, { COLORS, SPACING } from '../theme';
import { runBacktest } from '../api/client';
import { LineChart } from 'react-native-chart-kit';

const screenWidth = Dimensions.get('window').width;

const BacktestScreen = () => {
    // Initial state with two empty slots
    const [holdings, setHoldings] = useState([
        { symbol: '', allocation: '' },
        { symbol: '', allocation: '' }
    ]);
    const [duration, setDuration] = useState(3); // Years
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const addStock = () => {
        setHoldings([...holdings, { symbol: '', allocation: '' }]);
    };

    const updateHolding = (index, field, value) => {
        const newHoldings = [...holdings];
        newHoldings[index][field] = value;
        setHoldings(newHoldings);
    };

    const handleBacktest = async () => {
        // Filter and Validate
        const validHoldings = holdings
            .filter(h => h.symbol.trim() !== '' && h.allocation.trim() !== '')
            .map(h => ({
                symbol: h.symbol.toUpperCase().trim(),
                allocation: parseFloat(h.allocation)
            }));

        if (validHoldings.length === 0) {
            Alert.alert("Input Required", "Please enter at least one stock symbol.");
            return;
        }

        setLoading(true);
        setResult(null);
        try {
            const data = await runBacktest(validHoldings, duration);
            setResult(data);
        } catch (error) {
            Alert.alert("Time Travel Failed", "Could not fetch historical data.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <ScrollView style={styles.container}>
            {!result ? (
                // INPUT MODE
                <View>
                    <Text style={styles.headerTitle}>Time Travel</Text>
                    <Text style={styles.subTitle}>Simulate your strategy against historical market data.</Text>
                    
                    <View style={styles.card}>
                        {holdings.map((item, index) => (
                            <View key={index} style={styles.inputRow}>
                                <TextInput
                                    style={[styles.input, styles.symbolInput]}
                                    placeholder="Symbol (e.g. INFY)"
                                    placeholderTextColor={COLORS.textMuted}
                                    value={item.symbol}
                                    onChangeText={(text) => updateHolding(index, 'symbol', text)}
                                />
                                <TextInput
                                    style={[styles.input, styles.qtyInput]}
                                    placeholder="Alloc %"
                                    placeholderTextColor={COLORS.textMuted}
                                    keyboardType="numeric"
                                    value={item.allocation}
                                    onChangeText={(text) => updateHolding(index, 'allocation', text)}
                                />
                            </View>
                        ))}
                        
                        <TouchableOpacity style={styles.addButton} onPress={addStock}>
                            <Text style={styles.addButtonText}>+ Add Stock</Text>
                        </TouchableOpacity>

                        <Text style={styles.label}>Duration (Years)</Text>
                        <View style={styles.buttonRow}>
                            {[1, 3, 5, 10].map((y) => (
                                <TouchableOpacity
                                    key={y}
                                    style={[styles.optionButton, duration === y && styles.selectedOption]}
                                    onPress={() => setDuration(y)}
                                >
                                    <Text style={[styles.optionText, duration === y && styles.selectedText]}>{y}Y</Text>
                                </TouchableOpacity>
                            ))}
                        </View>

                        <TouchableOpacity style={styles.runButton} onPress={handleBacktest} disabled={loading}>
                            {loading ? (
                                <ActivityIndicator color="#FFF" />
                            ) : (
                                <Text style={styles.runText}>INITIATE SIMULATION</Text>
                            )}
                        </TouchableOpacity>
                    </View>
                </View>
            ) : (
                // RESULT MODE
                <View style={styles.resultContainer}>
                    <View style={styles.metricRow}>
                        <View style={styles.metricItem}>
                            <Text style={styles.metricLabel}>CAGR</Text>
                            <Text style={[styles.metricValue, { color: result.metrics.cagr_pct >= 0 ? COLORS.success : COLORS.danger }]}>
                                {result.metrics.cagr_pct}%
                            </Text>
                        </View>
                        <View style={styles.metricItem}>
                            <Text style={styles.metricLabel}>Max Drawdown</Text>
                            <Text style={[styles.metricValue, { color: COLORS.danger }]}>
                                {result.metrics.max_drawdown_pct}%
                            </Text>
                        </View>
                        <View style={styles.metricItem}>
                            <Text style={styles.metricLabel}>Final Value</Text>
                            <Text style={styles.metricValue}>
                                ₹{(result.metrics.final_value / 1000).toFixed(0)}k
                            </Text>
                        </View>
                    </View>

                    <Text style={styles.chartTitle}>Equity Curve (Growth of ₹1L)</Text>
                    <LineChart
                        data={{
                            labels: result.chart.labels,
                            datasets: [{ data: result.chart.data }]
                        }}
                        width={screenWidth - 48} // from react-native
                        height={220}
                        yAxisLabel="₹"
                        yAxisInterval={1}
                        chartConfig={{
                            backgroundColor: COLORS.surface,
                            backgroundGradientFrom: COLORS.surface,
                            backgroundGradientTo: COLORS.surface,
                            decimalPlaces: 0,
                            color: (opacity = 1) => `rgba(16, 185, 129, ${opacity})`, // Emerald Green
                            labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                            style: {
                                borderRadius: 16
                            },
                            propsForDots: {
                                r: "4",
                                strokeWidth: "2",
                                stroke: "#ffa726"
                            }
                        }}
                        bezier
                        style={{
                            marginVertical: 8,
                            borderRadius: 16
                        }}
                    />

                    <TouchableOpacity style={styles.resetButton} onPress={() => setResult(null)}>
                        <Text style={styles.resetText}>Run New Simulation</Text>
                    </TouchableOpacity>
                </View>
            )}
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
        padding: SPACING.l,
    },
    headerTitle: {
        fontSize: 28,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SPACING.s,
    },
    subTitle: {
        color: COLORS.textMuted,
        marginBottom: SPACING.l,
        fontSize: 14,
    },
    card: {
        backgroundColor: COLORS.surface,
        padding: SPACING.l,
        borderRadius: theme.borderRadius.m,
        marginBottom: SPACING.xl,
    },
    inputRow: {
        flexDirection: 'row',
        marginBottom: SPACING.m,
    },
    input: {
        backgroundColor: COLORS.background,
        color: COLORS.text,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.s,
        fontSize: 16,
    },
    symbolInput: {
        flex: 2,
        marginRight: SPACING.s,
    },
    qtyInput: {
        flex: 1,
    },
    addButton: {
        alignItems: 'center',
        padding: SPACING.s,
        marginBottom: SPACING.m,
    },
    addButtonText: {
        color: COLORS.primary,
        fontWeight: 'bold',
    },
    label: {
        color: COLORS.textMuted,
        marginBottom: SPACING.s,
        fontSize: 14,
    },
    buttonRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: SPACING.l,
    },
    optionButton: {
        flex: 1,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.s,
        borderWidth: 1,
        borderColor: COLORS.border,
        alignItems: 'center',
        marginHorizontal: 4,
    },
    selectedOption: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    optionText: {
        color: COLORS.textMuted,
        fontSize: 12,
        fontWeight: '600',
    },
    selectedText: {
        color: '#FFF',
    },
    runButton: {
        backgroundColor: COLORS.primary,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.s,
        alignItems: 'center',
    },
    runText: {
        color: '#FFF',
        fontWeight: 'bold',
        fontSize: 16,
    },
    resultContainer: {
        paddingBottom: SPACING.xl,
    },
    metricRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: SPACING.l,
        backgroundColor: COLORS.surface,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.m,
    },
    metricItem: {
        alignItems: 'center',
    },
    metricLabel: {
        color: COLORS.textMuted,
        fontSize: 12,
        marginBottom: 4,
    },
    metricValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    chartTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SPACING.m,
    },
    resetButton: {
        padding: SPACING.l,
        alignItems: 'center',
        marginTop: SPACING.m,
    },
    resetText: {
        color: COLORS.textMuted,
        textDecorationLine: 'underline',
    },
});

export default BacktestScreen;
