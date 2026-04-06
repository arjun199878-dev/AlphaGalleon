import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    SafeAreaView,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { COLORS, SPACING } from '../theme';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';

const LoginScreen = () => {
    const { login } = useAuth();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async () => {
        const trimmedName = name.trim();
        const trimmedEmail = email.trim().toLowerCase();

        if (!trimmedName) {
            Alert.alert('Required', 'Please enter your name.');
            return;
        }
        if (!trimmedEmail || !trimmedEmail.includes('@')) {
            Alert.alert('Required', 'Please enter a valid email address.');
            return;
        }

        setLoading(true);
        await login(trimmedName, trimmedEmail);
        setLoading(false);
    };

    return (
        <SafeAreaView style={styles.container}>
            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={styles.inner}
            >
                {/* Logo / Brand */}
                <View style={styles.brand}>
                    <View style={styles.logoRing}>
                        <Ionicons name="trending-up" size={36} color={COLORS.primary} />
                    </View>
                    <Text style={styles.appName}>AlphaGalleon</Text>
                    <Text style={styles.tagline}>Institutional-Grade Intelligence</Text>
                </View>

                {/* Form */}
                <View style={styles.form}>
                    <Text style={styles.formTitle}>Enter the Cockpit</Text>
                    <Text style={styles.formSubtitle}>
                        We'll remember you on this device. No password required.
                    </Text>

                    <View style={styles.inputWrapper}>
                        <Ionicons name="person-outline" size={18} color={COLORS.textMuted} style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder="Your name"
                            placeholderTextColor={COLORS.textMuted}
                            value={name}
                            onChangeText={setName}
                            autoCapitalize="words"
                            returnKeyType="next"
                        />
                    </View>

                    <View style={styles.inputWrapper}>
                        <Ionicons name="mail-outline" size={18} color={COLORS.textMuted} style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder="Email address"
                            placeholderTextColor={COLORS.textMuted}
                            value={email}
                            onChangeText={setEmail}
                            keyboardType="email-address"
                            autoCapitalize="none"
                            returnKeyType="done"
                            onSubmitEditing={handleLogin}
                        />
                    </View>

                    <TouchableOpacity
                        style={[styles.loginButton, loading && styles.loginButtonDisabled]}
                        onPress={handleLogin}
                        disabled={loading}
                        activeOpacity={0.8}
                    >
                        {loading ? (
                            <ActivityIndicator color="#000" />
                        ) : (
                            <Text style={styles.loginButtonText}>ENTER THE COCKPIT →</Text>
                        )}
                    </TouchableOpacity>
                </View>

                <Text style={styles.disclaimer}>
                    By continuing, you agree that this app provides analysis tools only and is not financial advice.
                </Text>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    inner: {
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: SPACING.l,
        paddingBottom: SPACING.xl,
    },
    brand: {
        alignItems: 'center',
        marginBottom: SPACING.xl * 1.5,
    },
    logoRing: {
        width: 80,
        height: 80,
        borderRadius: 40,
        borderWidth: 2,
        borderColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: SPACING.m,
        backgroundColor: 'rgba(19,236,91,0.08)',
    },
    appName: {
        fontSize: 32,
        fontWeight: '900',
        color: COLORS.text,
        letterSpacing: 1,
    },
    tagline: {
        fontSize: 13,
        color: COLORS.textMuted,
        marginTop: 4,
        letterSpacing: 2,
        textTransform: 'uppercase',
    },
    form: {
        backgroundColor: COLORS.surface,
        borderRadius: 20,
        borderWidth: 1,
        borderColor: COLORS.border,
        padding: SPACING.l,
        marginBottom: SPACING.l,
    },
    formTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: SPACING.s,
    },
    formSubtitle: {
        fontSize: 13,
        color: COLORS.textMuted,
        marginBottom: SPACING.l,
        lineHeight: 20,
    },
    inputWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.background,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: COLORS.border,
        paddingHorizontal: SPACING.m,
        marginBottom: SPACING.m,
        height: 52,
    },
    inputIcon: {
        marginRight: SPACING.s,
    },
    input: {
        flex: 1,
        color: COLORS.text,
        fontSize: 15,
    },
    loginButton: {
        backgroundColor: COLORS.primary,
        borderRadius: 12,
        height: 52,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: SPACING.s,
    },
    loginButtonDisabled: {
        opacity: 0.6,
    },
    loginButtonText: {
        color: '#000',
        fontWeight: '900',
        fontSize: 14,
        letterSpacing: 1.5,
    },
    disclaimer: {
        textAlign: 'center',
        color: COLORS.textMuted,
        fontSize: 11,
        lineHeight: 16,
        paddingHorizontal: SPACING.m,
    },
});

export default LoginScreen;
