import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export const THEMES = {
  kirkland: {
    id: 'kirkland', name: 'Kirkland & Ellis', desc: 'Black & White minimal', rank: '#1 Am Law',
    fontHeading: "'Source Sans 3', 'Inter', sans-serif",
    fontBody: "'Source Sans 3', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'light',
    bg: '#F0F0F0', bgAlt: '#E8E8E8', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#FFFFFF', sidebarText: '#6B6B6B', sidebarActiveText: '#111111',
    sidebarActiveBg: '#F0F0F0', sidebarAccent: '#111111',
    sidebarBorder: '#E5E5E5', sidebarLogo: '#111111',
    text: '#111111', textSecondary: '#6B6B6B',
    primary: '#111111', primaryFg: '#FFFFFF',
    accent: '#111111', accentLight: '#F0F0F0',
    buttonBg: '#111111', buttonText: '#FFFFFF',
    tagBg: '#F0F0F0', tagText: '#333333',
    searchBg: '#F5F5F5', border: '#E5E5E5', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  latham: {
    id: 'latham', name: 'Latham & Watkins', desc: 'Navy & deep blue', rank: '#2 Am Law',
    fontHeading: "'Libre Baskerville', Georgia, serif",
    fontBody: "'Source Sans 3', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'dark',
    bg: '#F0F2F5', bgAlt: '#E4E6EB', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#0F1D3A', sidebarText: '#8899B5', sidebarActiveText: '#FFFFFF',
    sidebarActiveBg: 'rgba(255,255,255,0.08)', sidebarAccent: '#5B9BD5',
    sidebarBorder: 'rgba(255,255,255,0.06)', sidebarLogo: '#FFFFFF',
    text: '#0F172A', textSecondary: '#65676B',
    primary: '#1E3A5F', primaryFg: '#FFFFFF',
    accent: '#1E3A5F', accentLight: '#EFF6FF',
    buttonBg: '#1E3A5F', buttonText: '#FFFFFF',
    tagBg: '#EFF6FF', tagText: '#1E3A5F',
    searchBg: '#F0F2F5', border: '#E4E6EB', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  skadden: {
    id: 'skadden', name: 'Skadden', desc: 'Bold red & white', rank: '#4 Am Law',
    fontHeading: "'DM Sans', 'Inter', sans-serif",
    fontBody: "'DM Sans', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'light',
    bg: '#F0F0F0', bgAlt: '#E8E8E8', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#FFFFFF', sidebarText: '#666666', sidebarActiveText: '#EE3224',
    sidebarActiveBg: '#FEF2F2', sidebarAccent: '#EE3224',
    sidebarBorder: '#E8E8E8', sidebarLogo: '#1A1A1A',
    text: '#1A1A1A', textSecondary: '#65676B',
    primary: '#EE3224', primaryFg: '#FFFFFF',
    accent: '#C41E1A', accentLight: '#FEF2F2',
    buttonBg: '#EE3224', buttonText: '#FFFFFF',
    tagBg: '#FEF2F2', tagText: '#B91C1C',
    searchBg: '#F5F5F5', border: '#E8E8E8', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  gibson: {
    id: 'gibson', name: 'Gibson Dunn', desc: 'Steel blue professional', rank: '#5 Am Law',
    fontHeading: "'Inter', sans-serif",
    fontBody: "'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'light',
    bg: '#F0F2F5', bgAlt: '#E4E6EB', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#FFFFFF', sidebarText: '#6B7280', sidebarActiveText: '#2563EB',
    sidebarActiveBg: '#EFF6FF', sidebarAccent: '#2563EB',
    sidebarBorder: '#E5E7EB', sidebarLogo: '#111827',
    text: '#111827', textSecondary: '#65676B',
    primary: '#2563EB', primaryFg: '#FFFFFF',
    accent: '#2563EB', accentLight: '#EFF6FF',
    buttonBg: '#2563EB', buttonText: '#FFFFFF',
    tagBg: '#EFF6FF', tagText: '#1D4ED8',
    searchBg: '#F0F2F5', border: '#E4E6EB', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  baker: {
    id: 'baker', name: 'Baker McKenzie', desc: 'Corporate teal', rank: '#8 Am Law',
    fontHeading: "'Work Sans', 'Inter', sans-serif",
    fontBody: "'Work Sans', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'light',
    bg: '#EFF2F1', bgAlt: '#E2E8E6', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#FFFFFF', sidebarText: '#5A7A72', sidebarActiveText: '#0D9488',
    sidebarActiveBg: '#F0FDFA', sidebarAccent: '#0D9488',
    sidebarBorder: '#D5E3E0', sidebarLogo: '#0F2E28',
    text: '#0F2E28', textSecondary: '#5A7A72',
    primary: '#0D9488', primaryFg: '#FFFFFF',
    accent: '#0D9488', accentLight: '#F0FDFA',
    buttonBg: '#0D9488', buttonText: '#FFFFFF',
    tagBg: '#F0FDFA', tagText: '#0F766E',
    searchBg: '#EFF2F1', border: '#D5E3E0', statusGreen: '#14B8A6',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  whitecase: {
    id: 'whitecase', name: 'White & Case', desc: 'Navy & gold classic', rank: '#9 Am Law',
    fontHeading: "'Cormorant Garamond', Georgia, serif",
    fontBody: "'Lato', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'dark',
    bg: '#F0EDE8', bgAlt: '#E5E0D8', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#1B2A4A', sidebarText: '#8F9FC0', sidebarActiveText: '#E8C563',
    sidebarActiveBg: 'rgba(232,197,99,0.08)', sidebarAccent: '#E8C563',
    sidebarBorder: 'rgba(255,255,255,0.06)', sidebarLogo: '#FFFFFF',
    text: '#1B2A4A', textSecondary: '#6B7A95',
    primary: '#1B2A4A', primaryFg: '#FFFFFF',
    accent: '#B8941F', accentLight: '#FDF8E8',
    buttonBg: '#1B2A4A', buttonText: '#FFFFFF',
    tagBg: '#FDF8E8', tagText: '#92740A',
    searchBg: '#F0EDE8', border: '#E5E0D8', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  dla: {
    id: 'dla', name: 'DLA Piper', desc: 'Deep green & slate', rank: '#3 Am Law',
    fontHeading: "'Noto Sans', 'Inter', sans-serif",
    fontBody: "'Noto Sans', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'light',
    bg: '#EFF1EF', bgAlt: '#E2E8E4', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#FFFFFF', sidebarText: '#5A7A68', sidebarActiveText: '#166534',
    sidebarActiveBg: '#F0FDF4', sidebarAccent: '#22C55E',
    sidebarBorder: '#DEE5DF', sidebarLogo: '#162B23',
    text: '#162B23', textSecondary: '#5A7A68',
    primary: '#166534', primaryFg: '#FFFFFF',
    accent: '#166534', accentLight: '#F0FDF4',
    buttonBg: '#166534', buttonText: '#FFFFFF',
    tagBg: '#F0FDF4', tagText: '#166534',
    searchBg: '#EFF1EF', border: '#DEE5DF', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
  ropes: {
    id: 'ropes', name: 'Ropes & Gray', desc: 'Burgundy & cream', rank: '#7 Am Law',
    fontHeading: "'Playfair Display', Georgia, serif",
    fontBody: "'Lato', 'Inter', sans-serif",
    fontMono: "'JetBrains Mono', monospace",
    sidebarStyle: 'dark',
    bg: '#F0EBE6', bgAlt: '#E5DDD6', card: '#FFFFFF', cardBorder: 'transparent',
    sidebar: '#3D1A2B', sidebarText: '#B88E9E', sidebarActiveText: '#FFFFFF',
    sidebarActiveBg: 'rgba(157,51,85,0.12)', sidebarAccent: '#E8A0B8',
    sidebarBorder: 'rgba(255,255,255,0.06)', sidebarLogo: '#FFFFFF',
    text: '#2D1A22', textSecondary: '#8C6B78',
    primary: '#7B2D47', primaryFg: '#FFFFFF',
    accent: '#7B2D47', accentLight: '#FDF2F6',
    buttonBg: '#7B2D47', buttonText: '#FFFFFF',
    tagBg: '#FDF2F6', tagText: '#7B2D47',
    searchBg: '#F0EBE6', border: '#E5DDD6', statusGreen: '#22C55E',
    cardShadow: '0 1px 2px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  },
};

const ThemeContext = createContext();

// Convert hex color to HSL string for Shadcn CSS variables (format: "H S% L%")
function hexToHSL(hex) {
  if (!hex || hex.startsWith('rgba') || hex.startsWith('rgb')) return null;
  hex = hex.replace('#', '');
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
  }
  return `${Math.round(h * 360)} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`;
}

export const ThemeProvider = ({ children }) => {
  const [themeId, setThemeId] = useState(() => localStorage.getItem('app_theme') || 'latham');
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('dark_mode') === 'true');
  const theme = THEMES[themeId] || THEMES.latham;

  // Toggle dark mode and persist to localStorage
  const toggleDarkMode = useCallback(() => {
    setDarkMode(prev => {
      const next = !prev;
      localStorage.setItem('dark_mode', String(next));
      return next;
    });
  }, []);

  // Apply dark mode class to html element
  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('app_theme', themeId);
    document.documentElement.classList.remove('dark');
    document.body.style.fontFamily = theme.fontBody;
    const root = document.documentElement;

    // Set custom --theme-* variables
    Object.entries({
      '--theme-font-heading': theme.fontHeading,
      '--theme-font-body': theme.fontBody,
      '--theme-font-mono': theme.fontMono,
      '--theme-bg': theme.bg, '--theme-bg-alt': theme.bgAlt,
      '--theme-card': theme.card, '--theme-card-border': theme.cardBorder,
      '--theme-sidebar': theme.sidebar, '--theme-sidebar-text': theme.sidebarText,
      '--theme-sidebar-active-text': theme.sidebarActiveText,
      '--theme-sidebar-active-bg': theme.sidebarActiveBg,
      '--theme-sidebar-accent': theme.sidebarAccent,
      '--theme-text': theme.text, '--theme-text-secondary': theme.textSecondary,
      '--theme-primary': theme.primary, '--theme-primary-fg': theme.primaryFg,
      '--theme-accent': theme.accent, '--theme-accent-light': theme.accentLight,
      '--theme-button-bg': theme.buttonBg, '--theme-button-text': theme.buttonText,
      '--theme-tag-bg': theme.tagBg, '--theme-tag-text': theme.tagText,
      '--theme-search-bg': theme.searchBg, '--theme-border': theme.border,
    }).forEach(([k, v]) => root.style.setProperty(k, v));

    // Bridge: Sync Shadcn/Tailwind CSS variables so all pages auto-theme
    const shadcnMap = {
      '--background': theme.bg,
      '--foreground': theme.text,
      '--card': theme.card,
      '--card-foreground': theme.text,
      '--popover': theme.card,
      '--popover-foreground': theme.text,
      '--primary': theme.primary,
      '--primary-foreground': theme.primaryFg,
      '--secondary': theme.bgAlt,
      '--secondary-foreground': theme.text,
      '--muted': theme.bgAlt,
      '--muted-foreground': theme.textSecondary,
      '--accent': theme.accentLight,
      '--accent-foreground': theme.text,
      '--destructive': '#EF4444',
      '--destructive-foreground': '#FAFAFA',
      '--border': theme.border,
      '--input': theme.border,
      '--ring': theme.primary,
    };
    Object.entries(shadcnMap).forEach(([k, v]) => {
      const hsl = hexToHSL(v);
      if (hsl) root.style.setProperty(k, hsl);
    });
  }, [themeId, theme]);

  return (
    <ThemeContext.Provider value={{ theme, themeId, setTheme: (id) => THEMES[id] && setThemeId(id), themes: THEMES, darkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
