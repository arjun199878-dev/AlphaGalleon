// Bulletproof Constants - These never change and cannot be undefined
export const COLORS = {
  primary: '#13ec5b',
  background: '#050505',
  surface: '#0A0A0A',
  surfaceLight: '#1A1A1A',
  text: '#E2E8F0',
  textMuted: '#64748B',
  border: 'rgba(255, 255, 255, 0.08)',
  success: '#13ec5b',
  danger: '#EF4444',
  error: '#EF4444',
  warning: '#F59E0B',
  secondary: '#6366F1',
};

export const SPACING = {
  xs: 4,
  s: 8,
  m: 16,
  l: 24,
  xl: 32,
};

export const BORDER_RADIUS = {
  s: 6,
  m: 12,
  l: 20,
};

const theme = {
  colors: COLORS,
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
};

export default theme;
