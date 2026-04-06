import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, ActivityIndicator, Dimensions } from 'react-native';
import theme, { COLORS, SPACING } from '../theme';
import { generatePortfolio } from '../api/client';
import { PieChart } from 'react-native-chart-kit';

const screenWidth = Dimensions.get('window').width;

const PortfolioScreen = () => {
    const [capital, setCapital] = useState('100000');
    const [risk, setRisk] = useState('Medium');
    const [horizon, setHorizon] = useState('3-5 Years');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const data = await generatePortfolio(parseFloat(capital), risk, horizon);
            setResult(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const getChartData = () => {
        if (!result) return [];
        const { allocation } = result.portfolio;
        
        // Convert "55%" to 55
        const parse = (val) => parseFloat(val.replace('%', ''));
        
        return [
            { name: 'Equity', population: parse(allocation.Equity), color: COLORS.primary, legendFontColor: COLORS.textMuted, legendFontSize: 12 },
            { name: 'Debt', population: parse(allocation.Debt), color: COLORS.success, legendFontColor: COLORS.textMuted, legendFontSize: 12 },
            { name: 'Gold', population: parse(allocation.Gold), color: '#FCD34D', legendFontColor: COLORS.textMuted, legendFontSize: 12 },
            { name: 'Cash', population: parse(allocation.Cash), color: COLORS.secondary, legendFontColor: COLORS.textMuted, legendFontSize: 12 },
        ].filter(item => item.population > 0);
    };

    return (
        <ScrollView style={styles.container}>
            <Text style={styles.headerTitle}>Portfolio Architect</Text>
            
            <View style={styles.card}>
                <Text style={styles.label}>Capital (₹)</Text>
                <TextInput
                    style={styles.input}
                    value={capital}
                    onChangeText={setCapital}
                    keyboardType="numeric"
                />

                <Text style={styles.label}>Risk Tolerance</Text>
                <View style={styles.buttonRow}>
                    {['Low', 'Medium', 'High'].map((r) => (
                        <TouchableOpacity
                            key={r}
                            style={[styles.optionButton, risk === r && styles.selectedOption]}
                            onPress={() => setRisk(r)}
                        >
                            <Text style={[styles.optionText, risk === r && styles.selectedText]}>{r}</Text>
                        </TouchableOpacity>
                    ))}
                </View>

                <Text style={styles.label}>Time Horizon</Text>
                <View style={styles.buttonRow}>
                    {['1 Year', '3-5 Years', '10+ Years'].map((h) => (
                        <TouchableOpacity
                            key={h}
                            style={[styles.optionButton, horizon === h && styles.selectedOption]}
                            onPress={() => setHorizon(h)}
                        >
                            <Text style={[styles.optionText, horizon === h && styles.selectedText]}>{h}</Text>
                        </TouchableOpacity>
                    ))}
                </View>

                <TouchableOpacity style={styles.generateButton} onPress={handleGenerate} disabled={loading}>
                    {loading ? (
                        <ActivityIndicator color="#FFF" />
                    ) : (
                        <Text style={styles.generateText}>ARCHITECT PORTFOLIO</Text>
                    )}
                </TouchableOpacity>
            </View>

            {result && (
                <View style={styles.resultContainer}>
                    <Text style={styles.strategyTitle}>{result.portfolio.strategy_name}</Text>
                    <Text style={styles.rationale}>{result.portfolio.rationale}</Text>

                    <View style={styles.chartContainer}>
                        <PieChart
                            data={getChartData()}
                            width={screenWidth - 48}
                            height={220}
                            chartConfig={{
                                color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
                            }}
                            accessor={"population"}
                            backgroundColor={"transparent"}
                            paddingLeft={"15"}
                            center={[10, 0]}
                            absolute
                        />
                    </View>

                    <Text style={styles.sectionHeader}>Top Picks</Text>
                    {result.portfolio.top_picks.map((pick, index) => (
                        <View key={index} style={styles.pickRow}>
                            <View style={styles.pickHeader}>
                                <Text style={styles.pickSymbol}>{pick.symbol}</Text>
                            </View>
                            <Text style={styles.pickReason}>{pick.reason}</Text>
                        </View>
                    ))}
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
        marginBottom: SPACING.l,
    },
    card: {
        backgroundColor: COLORS.surface,
        padding: SPACING.l,
        borderRadius: theme.borderRadius.m,
        marginBottom: SPACING.xl,
    },
    label: {
        color: COLORS.textMuted,
        marginBottom: SPACING.s,
        fontSize: 14,
    },
    input: {
        backgroundColor: COLORS.background,
        color: COLORS.text,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.s,
        marginBottom: SPACING.m,
        fontSize: 16,
    },
    buttonRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: SPACING.m,
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
    generateButton: {
        backgroundColor: COLORS.success,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.s,
        alignItems: 'center',
        marginTop: SPACING.m,
    },
    generateText: {
        color: '#FFF',
        fontWeight: 'bold',
        fontSize: 16,
    },
    resultContainer: {
        marginBottom: SPACING.xl,
    },
    strategyTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: SPACING.s,
    },
    rationale: {
        color: COLORS.text,
        lineHeight: 20,
        marginBottom: SPACING.l,
    },
    chartContainer: {
        alignItems: 'center',
        marginBottom: SPACING.l,
    },
    sectionHeader: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SPACING.m,
        marginTop: SPACING.s,
    },
    pickRow: {
        backgroundColor: COLORS.surface,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.m,
        marginBottom: SPACING.m,
    },
    pickHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: SPACING.s,
    },
    pickSymbol: {
        color: COLORS.text,
        fontWeight: 'bold',
        fontSize: 16,
    },
    pickReason: {
        color: COLORS.textMuted,
        fontSize: 14,
        lineHeight: 20,
    },
});

export default PortfolioScreen;
