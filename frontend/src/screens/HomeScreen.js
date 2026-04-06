import React, { useState, useEffect, useRef } from 'react';
import {
    View, Text, TextInput, TouchableOpacity, ScrollView,
    StyleSheet, ActivityIndicator, SafeAreaView, StatusBar,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import theme, { COLORS, SPACING } from '../theme';
import { getMarketPrice } from '../api/client';
import { useAuth } from '../context/AuthContext';

// Stocks displayed on the home grid
const FEATURED_STOCKS = [
    { symbol: 'RELIANCE', name: 'Reliance Industries', initial: 'R' },
    { symbol: 'TATASTEEL', name: 'Tata Steel', initial: 'T' },
    { symbol: 'INFY', name: 'Infosys', initial: 'I' },
    { symbol: 'HDFCBANK', name: 'HDFC Bank', initial: 'H' },
];

const IndexChip = ({ name, data, loading }) => (
    <View style={styles.indexItem}>
        <Text style={styles.indexName}>{name}</Text>
        <View style={styles.indexValueRow}>
            {loading ? (
                <ActivityIndicator size="small" color={COLORS.primary} />
            ) : (
                <>
                    <Text style={styles.indexValue}>
                        {data?.lastPrice ? data.lastPrice.toLocaleString('en-IN') : '—'}
                    </Text>
                    <Text style={[styles.indexChange, { color: (data?.change ?? 0) >= 0 ? COLORS.success : COLORS.danger }]}>
                        {data?.change >= 0 ? '+' : ''}{data?.change?.toFixed(2) ?? '—'}
                    </Text>
                </>
            )}
        </View>
    </View>
);

const StockMiniCard = ({ stock, priceData, loading, onPress }) => {
    const change = priceData?.change ?? 0;
    return (
        <TouchableOpacity style={styles.stockCard} onPress={onPress}>
            <View style={styles.stockIcon}>
                <Text style={styles.stockInitial}>{stock.initial}</Text>
            </View>
            <Text style={styles.stockName} numberOfLines={1}>{stock.name}</Text>
            {loading ? (
                <ActivityIndicator size="small" color={COLORS.primary} style={{ marginTop: 4 }} />
            ) : (
                <>
                    <Text style={styles.stockPrice}>
                        ₹{priceData?.lastPrice?.toLocaleString('en-IN') ?? '—'}
                    </Text>
                    <Text style={[styles.stockChange, { color: change >= 0 ? COLORS.success : COLORS.danger }]}>
                        {change >= 0 ? '+' : ''}{change.toFixed(2)} ({priceData?.pChange?.toFixed(2) ?? '0.00'}%)
                    </Text>
                </>
            )}
        </TouchableOpacity>
    );
};

const HomeScreen = ({ navigation }) => {
    const { user } = useAuth();
    const [searchQuery, setSearchQuery] = useState('');
    const searchRef = useRef(null);

    // Market indices state
    const [nifty, setNifty] = useState(null);
    const [sensex, setSensex] = useState(null);
    const [indicesLoading, setIndicesLoading] = useState(true);

    // Featured stocks state
    const [stockPrices, setStockPrices] = useState({});
    const [stocksLoading, setStocksLoading] = useState(true);

    const handleSearch = () => {
        if (searchQuery.trim()) {
            navigation.navigate('Memo', { symbol: searchQuery.toUpperCase().trim() });
        }
    };

    // Fetch indices on mount
    useEffect(() => {
        const fetchIndices = async () => {
            setIndicesLoading(true);
            try {
                const [n, s] = await Promise.allSettled([
                    getMarketPrice('NIFTY+50'),
                    getMarketPrice('SENSEX'),
                ]);
                if (n.status === 'fulfilled') setNifty(n.value);
                if (s.status === 'fulfilled') setSensex(s.value);
            } catch (_) { }
            finally { setIndicesLoading(false); }
        };
        fetchIndices();
    }, []);

    // Fetch featured stock prices on mount
    useEffect(() => {
        const fetchStocks = async () => {
            setStocksLoading(true);
            try {
                const results = await Promise.allSettled(
                    FEATURED_STOCKS.map(s => getMarketPrice(s.symbol))
                );
                const prices = {};
                results.forEach((r, i) => {
                    if (r.status === 'fulfilled' && r.value) {
                        prices[FEATURED_STOCKS[i].symbol] = r.value;
                    }
                });
                setStockPrices(prices);
            } catch (_) { }
            finally { setStocksLoading(false); }
        };
        fetchStocks();
    }, []);

    const greeting = () => {
        const h = new Date().getHours();
        if (h < 12) return 'Good morning';
        if (h < 17) return 'Good afternoon';
        return 'Good evening';
    };

    const firstLetter = user?.name?.[0]?.toUpperCase() ?? 'A';

    return (
        <SafeAreaView style={styles.safeArea}>
            <StatusBar barStyle="light-content" backgroundColor={COLORS.background} />
            <View style={styles.container}>
                {/* Header */}
                <View style={styles.header}>
                    <View>
                        <Text style={styles.headerGreeting}>{greeting()},</Text>
                        <Text style={styles.headerTitle}>{user?.name?.split(' ')[0] ?? 'Investor'}</Text>
                    </View>
                    <View style={styles.headerIcons}>
                        <TouchableOpacity style={styles.iconBtn} onPress={() => searchRef.current?.focus()}>
                            <Ionicons name="search" size={22} color={COLORS.textMuted} />
                        </TouchableOpacity>
                        <View style={styles.avatar}>
                            <Text style={styles.avatarText}>{firstLetter}</Text>
                        </View>
                    </View>
                </View>

                {/* Market Indices Bar */}
                <View style={styles.indicesRow}>
                    <IndexChip name="NIFTY 50" data={nifty} loading={indicesLoading} />
                    <View style={styles.indexDivider} />
                    <IndexChip name="SENSEX" data={sensex} loading={indicesLoading} />
                </View>

                {/* Tab Filter */}
                <View style={styles.tabRow}>
                    <TouchableOpacity style={[styles.tabItem, styles.activeTab]}>
                        <Text style={[styles.tabText, styles.activeTabText]}>Explore</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.tabItem} onPress={() => navigation.navigate('Tools', { screen: 'Portfolio' })}>
                        <Text style={styles.tabText}>Portfolio</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.tabItem} onPress={() => navigation.navigate('Tools', { screen: 'Doctor' })}>
                        <Text style={styles.tabText}>Doctor</Text>
                    </TouchableOpacity>
                </View>

                <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
                    {/* Search Bar */}
                    <View style={styles.searchBar}>
                        <Ionicons name="search-outline" size={20} color={COLORS.textMuted} style={{ marginRight: 10 }} />
                        <TextInput
                            ref={searchRef}
                            style={styles.searchInput}
                            placeholder="Search NSE symbol (e.g. INFY)"
                            placeholderTextColor={COLORS.textMuted}
                            value={searchQuery}
                            onChangeText={setSearchQuery}
                            onSubmitEditing={handleSearch}
                            autoCapitalize="characters"
                            returnKeyType="search"
                        />
                        {searchQuery.length > 0 && (
                            <TouchableOpacity onPress={handleSearch} style={styles.searchBtn}>
                                <Text style={styles.searchBtnText}>GO</Text>
                            </TouchableOpacity>
                        )}
                    </View>

                    {/* Most Bought Section */}
                    <Text style={styles.sectionTitle}>Market Overview</Text>
                    <View style={styles.cardGrid}>
                        {FEATURED_STOCKS.map(stock => (
                            <StockMiniCard
                                key={stock.symbol}
                                stock={stock}
                                priceData={stockPrices[stock.symbol]}
                                loading={stocksLoading}
                                onPress={() => navigation.navigate('Memo', { symbol: stock.symbol })}
                            />
                        ))}
                    </View>

                    {/* Products Section */}
                    <Text style={styles.sectionTitle}>Products & Tools</Text>
                    <View style={styles.productsRow}>
                        <TouchableOpacity style={styles.productItem} onPress={() => navigation.navigate('Tools')}>
                            <View style={styles.productIcon}><Ionicons name="grid" size={24} color={COLORS.primary} /></View>
                            <Text style={styles.productText}>All Tools</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.productItem} onPress={() => navigation.navigate('Tools', { screen: 'Portfolio' })}>
                            <View style={styles.productIcon}><Ionicons name="pie-chart" size={24} color="#6366F1" /></View>
                            <Text style={styles.productText}>Portfolio</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.productItem} onPress={() => navigation.navigate('Tools', { screen: 'Doctor' })}>
                            <View style={styles.productIcon}><Ionicons name="medkit" size={24} color="#F59E0B" /></View>
                            <Text style={styles.productText}>Doctor</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={styles.productItem} onPress={() => navigation.navigate('Tools', { screen: 'Backtest' })}>
                            <View style={styles.productIcon}><Ionicons name="time" size={24} color="#EF4444" /></View>
                            <Text style={styles.productText}>Backtest</Text>
                        </TouchableOpacity>
                    </View>
                </ScrollView>
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    safeArea: { flex: 1, backgroundColor: COLORS.background },
    container: { flex: 1, backgroundColor: COLORS.background },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: SPACING.l,
        paddingTop: SPACING.m,
        paddingBottom: SPACING.m,
    },
    headerGreeting: { fontSize: 13, color: COLORS.textMuted },
    headerTitle: { fontSize: 22, fontWeight: 'bold', color: COLORS.text },
    headerIcons: { flexDirection: 'row', alignItems: 'center', gap: 12 },
    iconBtn: {
        width: 38, height: 38, borderRadius: 19,
        backgroundColor: COLORS.surface,
        borderWidth: 1, borderColor: COLORS.border,
        justifyContent: 'center', alignItems: 'center',
    },
    avatar: {
        width: 38, height: 38, borderRadius: 19,
        backgroundColor: COLORS.primary,
        justifyContent: 'center', alignItems: 'center',
    },
    avatarText: { color: '#000', fontWeight: 'bold', fontSize: 16 },
    indicesRow: {
        flexDirection: 'row',
        paddingHorizontal: SPACING.l,
        paddingBottom: SPACING.m,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.border,
        alignItems: 'center',
    },
    indexDivider: { width: 1, height: 36, backgroundColor: COLORS.border, marginHorizontal: SPACING.l },
    indexItem: {},
    indexName: { fontSize: 11, color: COLORS.textMuted, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 1 },
    indexValueRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 2 },
    indexValue: { fontSize: 15, fontWeight: 'bold', color: COLORS.text },
    indexChange: { fontSize: 12 },
    tabRow: {
        flexDirection: 'row',
        paddingHorizontal: SPACING.l,
        paddingVertical: SPACING.m,
        gap: SPACING.l,
    },
    tabItem: { paddingBottom: 6 },
    activeTab: { borderBottomWidth: 2, borderBottomColor: COLORS.primary },
    tabText: { fontSize: 14, color: COLORS.textMuted, fontWeight: '600' },
    activeTabText: { color: COLORS.primary },
    content: { paddingHorizontal: SPACING.l, paddingBottom: 100 },
    searchBar: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surface,
        borderRadius: 10,
        paddingHorizontal: 12,
        paddingVertical: 10,
        marginBottom: SPACING.l,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    searchInput: { flex: 1, fontSize: 15, color: COLORS.text },
    searchBtn: {
        backgroundColor: COLORS.primary,
        paddingVertical: 4,
        paddingHorizontal: 10,
        borderRadius: 6,
    },
    searchBtnText: { color: '#000', fontWeight: 'bold', fontSize: 12 },
    sectionTitle: { fontSize: 17, fontWeight: 'bold', color: COLORS.text, marginBottom: SPACING.m },
    cardGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginBottom: SPACING.xl },
    stockCard: {
        width: '48%',
        backgroundColor: COLORS.surface,
        padding: 12,
        borderRadius: theme.borderRadius.m,
        borderWidth: 1,
        borderColor: COLORS.border,
        marginBottom: 12,
    },
    stockIcon: {
        width: 32, height: 32, borderRadius: 6,
        backgroundColor: COLORS.surfaceLight,
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 8,
    },
    stockInitial: { fontSize: 15, fontWeight: 'bold', color: COLORS.primary },
    stockName: { fontSize: 13, color: COLORS.textMuted, marginBottom: 4 },
    stockPrice: { fontSize: 15, fontWeight: 'bold', color: COLORS.text, marginBottom: 2 },
    stockChange: { fontSize: 11 },
    productsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: SPACING.xl },
    productItem: { alignItems: 'center' },
    productIcon: {
        width: 52, height: 52, borderRadius: 26,
        backgroundColor: COLORS.surface,
        borderWidth: 1, borderColor: COLORS.border,
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 8,
    },
    productText: { fontSize: 11, color: COLORS.textMuted, fontWeight: '600' },
});

export default HomeScreen;
