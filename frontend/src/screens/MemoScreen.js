import React, { useEffect, useState } from 'react';
import {
    View, Text, ScrollView, ActivityIndicator, StyleSheet,
    TouchableOpacity, Alert,
} from 'react-native';
import theme, { COLORS, SPACING } from '../theme';
import { getInvestmentMemo } from '../api/client';
import { useMutation } from 'convex/react';
import { api } from '../../../convex/_generated/api';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';

const MemoScreen = ({ route, navigation }) => {
    const { symbol } = route.params;
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [saved, setSaved] = useState(false);
    const [onWatchlist, setOnWatchlist] = useState(false);
    const [watchlistLoading, setWatchlistLoading] = useState(false);

    const storeMemo = useMutation(api.memos.store);
    const addToWatchlist = useMutation(api.watchlist.add);

    useEffect(() => {
        const fetchMemo = async () => {
            try {
                setLoading(true);
                setSaved(false);
                const result = await getInvestmentMemo(symbol);
                setData(result);

                // ── Auto-save memo to Convex ──────────────────────────────────────
                if (result?.memo) {
                    try {
                        await storeMemo({
                            userId: user?.userId ?? undefined,
                            symbol,
                            verdict: result.memo.verdict,
                            confidence: result.memo.risk_rating === 'LOW' ? 80 : result.memo.risk_rating === 'MEDIUM' ? 60 : 40,
                            summary: result.memo.summary,
                            reasoning: (result.memo.bull_case ?? []).join(' | '),
                            priceAtGeneration: result.market_data?.lastPrice ?? undefined,
                        });
                        setSaved(true);
                    } catch (convexErr) {
                        console.warn('Memo not saved to Convex (non-fatal):', convexErr);
                    }
                }
            } catch (err) {
                setError('Could not generate intel. Check your backend connection.');
            } finally {
                setLoading(false);
            }
        };

        fetchMemo();
    }, [symbol]);

    const handleAddWatchlist = async () => {
        if (!user?.userId) {
            Alert.alert('Not logged in', 'Please log in to use the watchlist.');
            return;
        }
        if (onWatchlist) return;
        setWatchlistLoading(true);
        try {
            await addToWatchlist({
                userId: user.userId,
                symbol,
                notes: data?.memo?.summary ?? '',
                targetPrice: undefined,
            });
            setOnWatchlist(true);
            Alert.alert('✅ Added', `${symbol} added to your watchlist.`);
        } catch (e) {
            Alert.alert('Error', 'Could not add to watchlist.');
        } finally {
            setWatchlistLoading(false);
        }
    };

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={styles.loadingText}>Synthesising Intelligence...</Text>
            </View>
        );
    }

    if (error || !data) {
        return (
            <View style={styles.errorContainer}>
                <Ionicons name="warning-outline" size={48} color={COLORS.danger} />
                <Text style={styles.errorText}>{error || 'Unknown Error'}</Text>
                <TouchableOpacity style={styles.retryBtn} onPress={() => {
                    setError(null);
                    setData(null);
                    setLoading(true);
                }}>
                    <Text style={styles.retryText}>Try Again</Text>
                </TouchableOpacity>
            </View>
        );
    }

    const { market_data, memo } = data;
    const { verdict, risk_rating, summary, bull_case, bear_case } = memo;
    const priceChange = market_data?.change ?? 0;

    const verdictColor =
        verdict === 'BUY' ? COLORS.success :
            verdict === 'SELL' ? COLORS.danger :
                COLORS.primary;

    return (
        <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
            {/* Header */}
            <View style={styles.header}>
                <View>
                    <Text style={styles.symbol}>{market_data?.symbol ?? symbol}</Text>
                    <Text style={styles.companyName}>{market_data?.companyName ?? ''}</Text>
                </View>
                <View style={styles.priceBlock}>
                    <Text style={styles.price}>₹{market_data?.lastPrice?.toLocaleString('en-IN') ?? '—'}</Text>
                    <Text style={[styles.change, { color: priceChange >= 0 ? COLORS.success : COLORS.danger }]}>
                        {priceChange >= 0 ? '+' : ''}{priceChange?.toFixed(2)} ({market_data?.pChange?.toFixed(2) ?? '0.00'}%)
                    </Text>
                </View>
            </View>

            {/* Save indicator */}
            {saved && (
                <View style={styles.savedBadge}>
                    <Ionicons name="checkmark-circle" size={14} color={COLORS.success} />
                    <Text style={styles.savedText}>Saved to history</Text>
                </View>
            )}

            {/* Verdict Card */}
            <View style={[styles.card, { borderLeftColor: verdictColor, borderLeftWidth: 4 }]}>
                <Text style={[styles.verdictTitle, { color: verdictColor }]}>{verdict}</Text>
                <Text style={styles.riskText}>Risk: {risk_rating}</Text>
                <Text style={styles.summaryText}>{summary}</Text>
            </View>

            {/* Bull Case */}
            <View style={styles.section}>
                <Text style={styles.sectionHeader}>🟢 Bull Thesis</Text>
                {(bull_case ?? []).map((point, index) => (
                    <View key={index} style={styles.bulletRow}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.bulletPoint}>{point}</Text>
                    </View>
                ))}
            </View>

            {/* Bear Case */}
            <View style={styles.section}>
                <Text style={styles.sectionHeader}>🔴 Bear Risks</Text>
                {(bear_case ?? []).map((point, index) => (
                    <View key={index} style={styles.bulletRow}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.bulletPoint}>{point}</Text>
                    </View>
                ))}
            </View>

            {/* Action Buttons */}
            <View style={styles.actions}>
                <TouchableOpacity
                    style={[styles.watchlistBtn, onWatchlist && styles.watchlistBtnActive]}
                    onPress={handleAddWatchlist}
                    disabled={watchlistLoading || onWatchlist}
                >
                    {watchlistLoading ? (
                        <ActivityIndicator size="small" color={COLORS.primary} />
                    ) : (
                        <>
                            <Ionicons name={onWatchlist ? 'bookmark' : 'bookmark-outline'} size={18} color={COLORS.primary} />
                            <Text style={styles.watchlistBtnText}>
                                {onWatchlist ? 'On Watchlist' : 'Add to Watchlist'}
                            </Text>
                        </>
                    )}
                </TouchableOpacity>
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background, padding: SPACING.l },
    loadingContainer: {
        flex: 1, justifyContent: 'center', alignItems: 'center',
        backgroundColor: COLORS.background,
    },
    loadingText: { marginTop: SPACING.m, color: COLORS.textMuted, fontSize: 14 },
    errorContainer: {
        flex: 1, justifyContent: 'center', alignItems: 'center',
        backgroundColor: COLORS.background, padding: SPACING.xl,
    },
    errorText: { color: COLORS.danger, textAlign: 'center', marginTop: SPACING.m, lineHeight: 22 },
    retryBtn: {
        marginTop: SPACING.l, borderWidth: 1, borderColor: COLORS.primary,
        borderRadius: theme.borderRadius.s, paddingVertical: 10, paddingHorizontal: SPACING.l,
    },
    retryText: { color: COLORS.primary, fontWeight: 'bold' },
    header: {
        flexDirection: 'row', justifyContent: 'space-between',
        alignItems: 'flex-start', marginBottom: SPACING.m,
    },
    symbol: { fontSize: 28, fontWeight: '900', color: COLORS.text },
    companyName: { fontSize: 14, color: COLORS.textMuted, marginTop: 2 },
    priceBlock: { alignItems: 'flex-end' },
    price: { fontSize: 22, fontWeight: 'bold', color: COLORS.text },
    change: { fontSize: 14, fontWeight: '600', marginTop: 2 },
    savedBadge: {
        flexDirection: 'row', alignItems: 'center', gap: 6,
        backgroundColor: 'rgba(19,236,91,0.08)',
        borderRadius: theme.borderRadius.s, paddingVertical: 6,
        paddingHorizontal: SPACING.m, marginBottom: SPACING.m,
        alignSelf: 'flex-start',
    },
    savedText: { color: COLORS.success, fontSize: 12, fontWeight: '600' },
    card: {
        backgroundColor: COLORS.surface,
        padding: SPACING.l,
        borderRadius: theme.borderRadius.m,
        marginBottom: SPACING.xl,
    },
    verdictTitle: { fontSize: 24, fontWeight: 'bold', marginBottom: SPACING.s },
    riskText: { color: COLORS.textMuted, marginBottom: SPACING.m, fontWeight: '600' },
    summaryText: { color: COLORS.text, fontSize: 15, lineHeight: 24 },
    section: { marginBottom: SPACING.xl },
    sectionHeader: {
        fontSize: 16, fontWeight: 'bold', color: COLORS.text,
        marginBottom: SPACING.m, borderBottomWidth: 1,
        borderBottomColor: COLORS.surfaceLight, paddingBottom: SPACING.s,
    },
    bulletRow: { flexDirection: 'row', marginBottom: SPACING.s, alignItems: 'flex-start' },
    bullet: { color: COLORS.primary, marginRight: 8, lineHeight: 22 },
    bulletPoint: { flex: 1, color: COLORS.textMuted, fontSize: 14, lineHeight: 22 },
    actions: { marginBottom: SPACING.xl },
    watchlistBtn: {
        flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
        gap: 8, borderWidth: 1, borderColor: COLORS.primary,
        borderRadius: theme.borderRadius.m, paddingVertical: 14,
        backgroundColor: 'rgba(19,236,91,0.06)',
    },
    watchlistBtnActive: {
        backgroundColor: 'rgba(19,236,91,0.14)',
        borderColor: COLORS.success,
    },
    watchlistBtnText: { color: COLORS.primary, fontWeight: 'bold', fontSize: 15 },
});

export default MemoScreen;
