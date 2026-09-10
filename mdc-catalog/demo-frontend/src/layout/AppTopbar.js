import Link from 'next/link';
import Image from 'next/image';
import React, { forwardRef, useContext, useImperativeHandle, useRef } from 'react';
import { LayoutContext } from './context/layoutcontext';
import { useAuth } from './context/AuthContext';
import { useTheme } from './context/ThemeContext';

const THEME_LABEL = {
    light: 'Light',
    dark: 'Dark',
    hmi: 'HMI'
};

const ThemeIcon = ({ theme }) => {
    if (theme === 'dark') {
        return (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" />
            </svg>
        );
    }
    if (theme === 'hmi') {
        return (
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3 5h6v6H3zM3 13h6v6H3zM11 5h10v6H11zM11 13h10v6H11z" />
            </svg>
        );
    }
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
        </svg>
    );
};

// eslint-disable-next-line react/display-name
const AppTopbar = forwardRef((_, ref) => {
    const menubuttonRef = useRef(null);
    const topbarmenuRef = useRef(null);
    const topbarmenubuttonRef = useRef(null);
    const { onMenuToggle, layoutState, showProfileSidebar, setLayoutState } = useContext(LayoutContext);
    const { authenticated, login, logout, userName } = useAuth();
    const { theme, cycleTheme } = useTheme();

    useImperativeHandle(ref, () => ({
        menubutton: menubuttonRef.current,
        topbarmenu: topbarmenuRef.current,
        topbarmenubutton: topbarmenubuttonRef.current
    }));

    const handleProfileAction = () => {
        if (!authenticated) {
            login().catch((error) => {
                console.error('Error during login:', error);
            });
            return;
        }

        showProfileSidebar();
    };

    const handleLogout = () => {
        setLayoutState((prevLayoutState) => ({ ...prevLayoutState, profileSidebarVisible: false }));
        logout().catch((error) => {
            console.error('Error during logout:', error);
        });
    };

    return (
        <header className="layout-topbar">
            <button
                ref={menubuttonRef}
                type="button"
                className="p-link layout-menu-button layout-topbar-button"
                onClick={onMenuToggle}
                aria-label="Toggle navigation menu"
            >
                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path d="M4 7h16" />
                    <path d="M4 12h12" />
                    <path d="M4 17h16" />
                </svg>
            </button>
            <Link href="/" className="layout-topbar-logo">
                <Image
                    src="/layout/images/MaaSAI_colour_main_letters.png"
                    alt="MaaSAI"
                    width={140}
                    height={32}
                    priority
                />
            </Link>
            <div ref={topbarmenuRef} className="layout-topbar-menu">
                <button
                    type="button"
                    className="p-link layout-topbar-button layout-topbar-theme"
                    onClick={cycleTheme}
                    aria-label={`Switch theme (current: ${THEME_LABEL[theme]})`}
                    title={`Theme: ${THEME_LABEL[theme]} — click to cycle`}
                >
                    <ThemeIcon theme={theme} />
                </button>
                <button
                    ref={topbarmenubuttonRef}
                    type="button"
                    className="p-link layout-topbar-profile"
                    onClick={handleProfileAction}
                    aria-label={authenticated ? 'Logout' : 'Login'}
                    title={authenticated ? 'Logout' : 'Login'}
                >
                    {!authenticated ? (
                        <>
                            <span className="layout-topbar-profile__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24">
                                    <path d="M12 12a3.25 3.25 0 1 0-3.25-3.25A3.25 3.25 0 0 0 12 12Zm0 1.75c-3.39 0-6.25 1.72-6.25 4.25a.75.75 0 0 0 1.5 0c0-1.39 1.98-2.75 4.75-2.75s4.75 1.36 4.75 2.75a.75.75 0 0 0 1.5 0c0-2.53-2.86-4.25-6.25-4.25Z" />
                                </svg>
                            </span>
                            <span className="layout-topbar-profile__label">Login</span>
                        </>
                    ) : (
                        <>
                            <span className="layout-topbar-profile__label">{userName || 'User'}</span>
                            <span className="layout-topbar-profile__caret" aria-hidden="true">▾</span>
                        </>
                    )}
                </button>
                {authenticated && layoutState.profileSidebarVisible ? (
                    <div className="layout-topbar-dropdown">
                        <button type="button" className="layout-topbar-dropdown__item" onClick={handleLogout}>
                            Logout
                        </button>
                    </div>
                ) : null}
            </div>
        </header>
    );
});

export default AppTopbar;
