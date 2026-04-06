import React from 'react';
import {
    View, Text, ScrollView, StyleSheet, TouchableOpacity,
    Alert, ActivityIndicator, SafeAreaView, StatusBar,
} from 'react-native';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../../convex/_generated/api';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import theme, { COLORS, SPACING } from '../theme';

// ── Verdict badge colour helper ────────────────────────────────────────────
const verdictColor = (v) => v === 'BUY' ? COLORS.success : v === 'SELL' ? COLORS.danger : COLORS.primary;

// ── Recent Memo Card ───────────────────────────────────────────────────────
const MemoCard = ({ memo }) => (
    <View style={styles.memoCard}>
        <View style={styles.memoTop}>
            <Text style={styles.memoSymbol}>{memo.symbol}</Text>
            <View style={[styles.verdictBadge, { backgroundColor: verdictColor(memo.verdict) + '22', borderColor: verdictColor(memo.verdict) }]}>
                <Text style={[styles.verdictText, { color: verdictColor(memo.verdict) }]}>{memo.verdict}</Text>
            </View>
        </View>
        <Text style={styles.memoSummary} numberOfLines={2}>{memo.summary}</Text>
        <Text style={styles.memoDate}>
            {new Date(memo.generatedAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
            {memo.priceAtGeneration ? `  ·  ₹${memo.priceAtGeneration.toLocaleString('en-IN')}` : ''}
        </Text>
    </View>
);

// ── Watchlist Row ──────────────────────────────────────────────────────────
const WatchlistRow = ({ item, onRemove }) => (
    <View style={styles.watchRow}>
        <View style={styles.watchIcon}>
            <Text style={styles.watchInitial}>{item.symbol[0]}</Text>
        </View>
        <View style={styles.watchInfo}>
            <Text style={styles.watchSymbol}>{item.symbol}</Text>
            {item.notes ? <Text style={styles.watchNote} numberOfLines={1}>{item.notes}</Text> : null}
        </View>
        <TouchableOpacity onPress={onRemove} style={styles.removeBtn} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
            <Ionicons name="trash-outline" size={18} color={COLORS.danger} />
        </TouchableOpacity>
    </View>
);

// ── Main Profile Screen ────────────────────────────────────────────────────
const ProfileScreen = () => {
    const { user, logout } = useAuth();

    const memos = useQuery(
        api.memos.listByUser,
        user?.userId ? { userId: user.userId } : 'skip'
    );

    const watchlist = useQuery(
        api.watchlist.listByUser,
        user?.userId ? { userId: user.userId } : 'skip'
    );

    const removeFromWatchlist = useMutation(api.watchlist.remove);

    const handleRemoveWatch = (id, symbol) => {
        Alert.alert('Remove', `Remove ${symbol} from watchlist?`, [
            { text: 'Cancel', style: 'cancel' },
            {
                text: 'Remove', style: 'destructive',
                onPress: () => removeFromWatchlist({ id }),
            },
        ]);
    };

    const handleLogout = () => {
        Alert.alert('Log Out', 'Are you sure?', [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Log Out', style: 'destructive', onPress: logout },
        ]);
    };

    const firstLetter = user?.name?.[0]?.toUpperCase() ?? 'A';
    const initials = user?.name
        ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
        : 'AG';

    return (
        <SafeAreaView style={styles.safe}>
            <StatusBar barStyle="light-content" backgroundColor={COLORS.background} />
            <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>

                {/* ── Hero Header ── */}
                <View style={styles.hero}>
                    <View style={styles.avatarCircle}>
                        <Text style={styles.avatarText}>{initials}</Text>
                    </View>
                    <Text style={styles.userName}>{user?.name ?? 'Investor'}</Text>
                    <Text style={styles.userEmail}>{user?.email ?? ''}</Text>
                    <View style={styles.sessionBadge}>
                        <View style={styles.onlineDot} />
                        <Text style={styles.sessionText}>Session Active</Text>
                    </View>
                </View>

                {/* ── Recent Memos ── */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Recent Analysis</Text>
                    {memos === undefined ? (
                        <ActivityIndicator color={COLORS.primary} style={{ marginTop: SPACING.m }} />
                    ) : memos === null || memos.length === 0 ? (
                        <View style={styles.emptyState}>
                            <Ionicons name="document-outline" size={32} color={COLORS.textMuted} />
                            <Text style={styles.emptyText}>No memos yet. Search a stock to generate one.</Text>
                        </View>
                    ) : (
                        memos.slice(0, 5).map(memo => <MemoCard key={memo._id} memo={memo} />)
                    )}
                </View>

                {/* ── Watchlist ── */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Watchlist</Text>
                    {watchlist === undefined ? (
                        <ActivityIndicator color={COLORS.primary} style={{ marginTop: SPACING.m }} />
                    ) : !watchlist || watchlist.length === 0 ? (
                        <View style={styles.emptyState}>
                            <Ionicons name="bookmark-outline" size={32} color={COLORS.textMuted} />
                            <Text style={styles.emptyText}>No stocks on your watchlist. Add one from a Memo.</Text>
                        </View>
                    ) : (
                        <View style={styles.watchCard}>
                            {watchlist.map((item, i) => (
                                <WatchlistRow
                                    key={item._id}
                                    item={item}
                                    onRemove={() => handleRemoveWatch(item._id, item.symbol)}
                                />
                            ))}
                        </View>
                    )}
                </View>

                {/* ── Menu ── */}
                <View style={styles.menu}>
                    <TouchableOpacity style={styles.menuItem}>
                        <Ionicons name="shield-checkmark-outline" size={20} color={COLORS.textMuted} style={styles.menuIcon} />
                        <Text style={styles.menuText}>Data & Privacy</Text>
                        <Ionicons name="chevron-forward" size={16} color={COLORS.textMuted} />
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.menuItem}>
                        <Ionicons name="help-circle-outline" size={20} color={COLORS.textMuted} style={styles.menuIcon} />
                        <Text style={styles.menuText}>Help & Support</Text>
                        <Ionicons name="chevron-forward" size={16} color={COLORS.textMuted} />
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.menuItem}>
                        <Ionicons name="information-circle-outline" size={20} color={COLORS.textMuted} style={styles.menuIcon} />
                        <Text style={styles.menuText}>About AlphaGalleon</Text>
                        <Ionicons name="chevron-forward" size={16} color={COLORS.textMuted} />
                    </TouchableOpacity>
                </View>

                {/* ── Logout ── */}
                <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
                    <Ionicons name="log-out-outline" size={18} color={COLORS.danger} />
                    <Text style={styles.logoutText}>Log Out</Text>
                </TouchableOpacity>

                <Text style={styles.disclaimer}>
                    AlphaGalleon provides analysis tools only. Nothing here is financial advice.
                </Text>
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    safe: { flex: 1, backgroundColor: COLORS.background },
    container: { flex: 1, backgroundColor: COLORS.background },

    // Hero
    hero: { alignItems: 'center', paddingVertical: SPACING.xl, paddingHorizontal: SPACING.l, borderBottomWidth: 1, borderBottomColor: COLORS.border },
    avatarCircle: {
        width: 80, height: 80, borderRadius: 40,
        backgroundColor: COLORS.primary,
        justifyContent: 'center', alignItems: 'center',
        marginBottom: SPACING.m,
    },
    avatarText: { fontSize: 28, fontWeight: '900', color: '#000' },
    userName: { fontSize: 22, fontWeight: 'bold', color: COLORS.text },
    userEmail: { fontSize: 13, color: COLORS.textMuted, marginTop: 4 },
    sessionBadge: {
        flexDirection: 'row', alignItems: 'center', gap: 6,
        marginTop: SPACING.m, backgroundColor: 'rgba(19,236,91,0.08)',
        borderRadius: 20, paddingVertical: 4, paddingHorizontal: 12,
    },
    onlineDot: { width: 7, height: 7, borderRadius: 4, backgroundColor: COLORS.primary },
    sessionText: { fontSize: 11, color: COLORS.primary, fontWeight: '600' },

    // Sections
    section: { paddingHorizontal: SPACING.l, paddingTop: SPACING.xl },
    sectionTitle: { fontSize: 17, fontWeight: 'bold', color: COLORS.text, marginBottom: SPACING.m },

    // Memo card
    memoCard: {
        backgroundColor: COLORS.surface, borderRadius: theme.borderRadius.m,
        borderWidth: 1, borderColor: COLORS.border,
        padding: SPACING.m, marginBottom: SPACING.m,
    },
    memoTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
    memoSymbol: { fontSize: 16, fontWeight: 'bold', color: COLORS.text },
    verdictBadge: {
        paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6,
        borderWidth: 1,
    },
    verdictText: { fontSize: 11, fontWeight: 'bold' },
    memoSummary: { fontSize: 13, color: COLORS.textMuted, lineHeight: 19, marginBottom: 6 },
    memoDate: { fontSize: 11, color: COLORS.textMuted },

    // Watchlist
    watchCard: {
        backgroundColor: COLORS.surface, borderRadius: theme.borderRadius.m,
        borderWidth: 1, borderColor: COLORS.border, overflow: 'hidden',
    },
    watchRow: {
        flexDirection: 'row', alignItems: 'center', padding: SPACING.m,
        borderBottomWidth: 1, borderBottomColor: COLORS.border,
    },
    watchIcon: {
        width: 36, height: 36, borderRadius: 18,
        backgroundColor: COLORS.surfaceLight,
        justifyContent: 'center', alignItems: 'center', marginRight: SPACING.m,
    },
    watchInitial: { fontSize: 15, fontWeight: 'bold', color: COLORS.primary },
    watchInfo: { flex: 1 },
    watchSymbol: { fontSize: 15, fontWeight: 'bold', color: COLORS.text },
    watchNote: { fontSize: 12, color: COLORS.textMuted, marginTop: 2 },
    removeBtn: { padding: 4 },

    // Empty state
    emptyState: { alignItems: 'center', paddingVertical: SPACING.xl },
    emptyText: { color: COLORS.textMuted, fontSize: 13, marginTop: SPACING.m, textAlign: 'center', lineHeight: 20 },

    // Menu
    menu: {
        marginTop: SPACING.xl, marginHorizontal: SPACING.l,
        backgroundColor: COLORS.surface, borderRadius: theme.borderRadius.m,
        borderWidth: 1, borderColor: COLORS.border, overflow: 'hidden',
    },
    menuItem: {
        flexDirection: 'row', alignItems: 'center', padding: SPACING.m,
        borderBottomWidth: 1, borderBottomColor: COLORS.border,
    },
    menuIcon: { marginRight: SPACING.m },
    menuText: { flex: 1, fontSize: 15, color: COLORS.text },

    // Logout
    logoutBtn: {
        flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
        gap: 8, margin: SPACING.l, padding: SPACING.m,
        borderWidth: 1, borderColor: COLORS.danger, borderRadius: theme.borderRadius.m,
        backgroundColor: 'rgba(239,68,68,0.06)',
    },
    logoutText: { color: COLORS.danger, fontWeight: 'bold', fontSize: 15 },

    disclaimer: {
        textAlign: 'center', color: COLORS.textMuted, fontSize: 11,
        paddingHorizontal: SPACING.l, paddingBottom: SPACING.xl, lineHeight: 16,
    },
});

export default ProfileScreen;
