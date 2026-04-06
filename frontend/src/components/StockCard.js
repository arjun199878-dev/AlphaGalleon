import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import theme from '../theme';

const StockCard = ({ symbol, price, change, percentChange, verdict, onPress }) => {
    // Determine color based on verdict or change
    let changeColor = theme.colors.textMuted;
    if (percentChange > 0) changeColor = theme.colors.success;
    if (percentChange < 0) changeColor = theme.colors.danger;

    let verdictColor = theme.colors.textMuted;
    if (verdict === 'BUY') verdictColor = theme.colors.success;
    if (verdict === 'SELL') verdictColor = theme.colors.danger;
    if (verdict === 'HOLD') verdictColor = theme.colors.primary;

    return (
        <TouchableOpacity style={styles.card} onPress={onPress}>
            <View style={styles.header}>
                <Text style={styles.symbol}>{symbol}</Text>
                {verdict && (
                    <View style={[styles.badge, { backgroundColor: verdictColor }]}>
                        <Text style={styles.verdictText}>{verdict}</Text>
                    </View>
                )}
            </View>
            <View style={styles.body}>
                <Text style={styles.price}>₹{price}</Text>
                <Text style={[styles.change, { color: changeColor }]}>
                    {percentChange > 0 ? '+' : ''}{percentChange}%
                </Text>
            </View>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: theme.colors.surface,
        borderRadius: theme.borderRadius.l,
        padding: theme.spacing.m,
        marginBottom: theme.spacing.m,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: theme.spacing.s,
    },
    symbol: {
        fontSize: 18,
        fontWeight: 'bold',
        color: theme.colors.text,
    },
    badge: {
        paddingVertical: 4,
        paddingHorizontal: 8,
        borderRadius: theme.borderRadius.s,
    },
    verdictText: {
        color: '#FFFFFF',
        fontWeight: 'bold',
        fontSize: 12,
    },
    body: {
        flexDirection: 'row',
        alignItems: 'baseline',
        justifyContent: 'space-between',
    },
    price: {
        fontSize: 24,
        fontWeight: 'bold',
        color: theme.colors.text,
    },
    change: {
        fontSize: 14,
        fontWeight: '600',
    },
});

export default StockCard;
