import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import theme, { COLORS, SPACING } from '../theme';
import { diagnosePortfolio } from '../api/client';

const DoctorScreen = () => {
    // Initial state with two empty slots
    const [holdings, setHoldings] = useState([
        { symbol: '', quantity: '' },
        { symbol: '', quantity: '' }
    ]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const addStock = () => {
        setHoldings([...holdings, { symbol: '', quantity: '' }]);
    };

    const updateHolding = (index, field, value) => {
        const newHoldings = [...holdings];
        newHoldings[index][field] = value;
        setHoldings(newHoldings);
    };

    const handleDiagnose = async () => {
        // Filter out empty entries
        const validHoldings = holdings
            .filter(h => h.symbol.trim() !== '')
            .map(h => ({
                symbol: h.symbol.toUpperCase().trim(),
                quantity: parseInt(h.quantity) || 1
            }));

        if (validHoldings.length === 0) {
            Alert.alert("Input Required", "Please enter at least one stock symbol.");
            return;
        }

        setLoading(true);
        setResult(null);
        try {
            const data = await diagnosePortfolio(validHoldings);
            setResult(data);
        } catch (error) {
            Alert.alert("Diagnosis Failed", "Could not connect to The Doctor.");
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return COLORS.success;
        if (score >= 50) return COLORS.primary;
        return COLORS.danger;
    };

    return (
        <ScrollView style={styles.container}>
            {!result ? (
                // INPUT MODE
                <View>
                    <Text style={styles.headerTitle}>Portfolio Checkup</Text>
                    <Text style={styles.subTitle}>Enter your current holdings for a ruthless institutional diagnosis.</Text>
                    
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
                                    placeholder="Qty"
                                    placeholderTextColor={COLORS.textMuted}
                                    keyboardType="numeric"
                                    value={item.quantity}
                                    onChangeText={(text) => updateHolding(index, 'quantity', text)}
                                />
                            </View>
                        ))}
                        
                        <TouchableOpacity style={styles.addButton} onPress={addStock}>
                            <Text style={styles.addButtonText}>+ Add Stock</Text>
                        </TouchableOpacity>

                        <TouchableOpacity style={styles.diagnoseButton} onPress={handleDiagnose} disabled={loading}>
                            {loading ? (
                                <ActivityIndicator color="#FFF" />
                            ) : (
                                <Text style={styles.diagnoseText}>RUN DIAGNOSIS</Text>
                            )}
                        </TouchableOpacity>
                    </View>
                </View>
            ) : (
                // RESULT MODE
                <View style={styles.resultContainer}>
                    <View style={styles.scoreCard}>
                        <Text style={styles.scoreTitle}>Health Score</Text>
                        <Text style={[styles.scoreValue, { color: getScoreColor(parseInt(result.diagnosis.health_score)) }]}>
                            {result.diagnosis.health_score}/100
                        </Text>
                        <Text style={styles.riskLabel}>Risk Level: {result.diagnosis.risk_level}</Text>
                    </View>

                    <View style={styles.section}>
                        <Text style={styles.sectionHeader}>Doctor's Summary</Text>
                        <Text style={styles.bodyText}>{result.diagnosis.diagnosis_summary}</Text>
                    </View>

                    {result.diagnosis.critical_warnings.length > 0 && (
                        <View style={styles.warningCard}>
                            <Text style={styles.warningTitle}>⚠️ CRITICAL WARNINGS</Text>
                            {result.diagnosis.critical_warnings.map((warn, i) => (
                                <Text key={i} style={styles.warningText}>• {warn}</Text>
                            ))}
                        </View>
                    )}

                    <View style={styles.section}>
                        <Text style={styles.sectionHeader}>Prescriptions</Text>
                        {result.diagnosis.prescriptions.map((rx, i) => (
                            <View key={i} style={styles.rxCard}>
                                <View style={styles.rxHeader}>
                                    <Text style={styles.rxSymbol}>{rx.symbol}</Text>
                                    <View style={[
                                        styles.rxBadge, 
                                        { backgroundColor: rx.action.includes('SELL') ? COLORS.danger : COLORS.success }
                                    ]}>
                                        <Text style={styles.rxAction}>{rx.action}</Text>
                                    </View>
                                </View>
                                <Text style={styles.rxReason}>{rx.reason}</Text>
                            </View>
                        ))}
                    </View>

                    <TouchableOpacity style={styles.resetButton} onPress={() => setResult(null)}>
                        <Text style={styles.resetText}>Check Another Portfolio</Text>
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
        marginBottom: SPACING.l,
    },
    addButtonText: {
        color: COLORS.primary,
        fontWeight: 'bold',
    },
    diagnoseButton: {
        backgroundColor: COLORS.danger, // Red for medical emergency vibe
        padding: SPACING.m,
        borderRadius: theme.borderRadius.s,
        alignItems: 'center',
    },
    diagnoseText: {
        color: '#FFF',
        fontWeight: 'bold',
        fontSize: 16,
    },
    scoreCard: {
        alignItems: 'center',
        marginBottom: SPACING.xl,
        backgroundColor: COLORS.surface,
        padding: SPACING.l,
        borderRadius: theme.borderRadius.l,
    },
    scoreTitle: {
        color: COLORS.textMuted,
        fontSize: 16,
        marginBottom: SPACING.s,
    },
    scoreValue: {
        fontSize: 48,
        fontWeight: '900',
        marginBottom: SPACING.s,
    },
    riskLabel: {
        color: COLORS.text,
        fontSize: 18,
        fontWeight: 'bold',
    },
    section: {
        marginBottom: SPACING.xl,
    },
    sectionHeader: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SPACING.m,
    },
    bodyText: {
        color: COLORS.text,
        fontSize: 16,
        lineHeight: 24,
    },
    warningCard: {
        backgroundColor: 'rgba(239, 68, 68, 0.1)', // Red transparent
        padding: SPACING.m,
        borderRadius: theme.borderRadius.m,
        marginBottom: SPACING.xl,
        borderLeftWidth: 4,
        borderLeftColor: COLORS.danger,
    },
    warningTitle: {
        color: COLORS.danger,
        fontWeight: 'bold',
        marginBottom: SPACING.s,
    },
    warningText: {
        color: COLORS.danger,
        marginBottom: 4,
    },
    rxCard: {
        backgroundColor: COLORS.surface,
        padding: SPACING.m,
        borderRadius: theme.borderRadius.m,
        marginBottom: SPACING.m,
    },
    rxHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: SPACING.s,
    },
    rxSymbol: {
        color: COLORS.text,
        fontWeight: 'bold',
        fontSize: 18,
    },
    rxBadge: {
        paddingVertical: 4,
        paddingHorizontal: 8,
        borderRadius: 4,
    },
    rxAction: {
        color: '#FFF',
        fontWeight: 'bold',
        fontSize: 12,
    },
    rxReason: {
        color: COLORS.textMuted,
        fontSize: 14,
    },
    resetButton: {
        padding: SPACING.l,
        alignItems: 'center',
    },
    resetText: {
        color: COLORS.textMuted,
        textDecorationLine: 'underline',
    },
});

export default DoctorScreen;
