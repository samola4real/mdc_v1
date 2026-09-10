import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

export const THEMES = ['light', 'dark', 'hmi'];
const STORAGE_KEY = 'maasai.theme';
const DEFAULT_THEME = 'light';

const THEME_STYLESHEETS = {
    light: '/themes/lara-light-indigo/theme.css',
    dark: '/themes/lara-dark-indigo/theme.css',
    hmi: '/themes/lara-dark-amber/theme.css'
};

const applyThemeStylesheet = (theme) => {
    if (typeof document === 'undefined') return;
    const link = document.getElementById('theme-css');
    if (!link) return;
    const next = THEME_STYLESHEETS[theme] || THEME_STYLESHEETS[DEFAULT_THEME];
    if (link.getAttribute('href') !== next) {
        link.setAttribute('href', next);
    }
};

const isValidTheme = (value) => THEMES.includes(value);

const readStoredTheme = () => {
    if (typeof window === 'undefined') {
        return DEFAULT_THEME;
    }
    try {
        const stored = window.localStorage.getItem(STORAGE_KEY);
        return isValidTheme(stored) ? stored : DEFAULT_THEME;
    } catch {
        return DEFAULT_THEME;
    }
};

export const ThemeProvider = ({ children }) => {
    const [theme, setThemeState] = useState(DEFAULT_THEME);

    // Hydrate from localStorage after mount (avoids SSR mismatch)
    useEffect(() => {
        setThemeState(readStoredTheme());
    }, []);

    // Apply theme to <html> via data-theme attribute, swap PrimeReact
    // stylesheet, and persist the choice.
    useEffect(() => {
        if (typeof document === 'undefined') return;
        document.documentElement.setAttribute('data-theme', theme);
        applyThemeStylesheet(theme);
        try {
            window.localStorage.setItem(STORAGE_KEY, theme);
        } catch {
            /* ignore quota errors */
        }
    }, [theme]);

    const setTheme = (next) => {
        if (isValidTheme(next)) {
            setThemeState(next);
        }
    };

    const cycleTheme = () => {
        const idx = THEMES.indexOf(theme);
        setThemeState(THEMES[(idx + 1) % THEMES.length]);
    };

    return (
        <ThemeContext.Provider value={{ theme, setTheme, cycleTheme, themes: THEMES }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const ctx = useContext(ThemeContext);
    if (!ctx) {
        // Defensive default so consumers can mount before provider is ready (SSR).
        return { theme: DEFAULT_THEME, setTheme: () => {}, cycleTheme: () => {}, themes: THEMES };
    }
    return ctx;
};
