import React, { createContext, useContext, useEffect, useState } from 'react';
import { getKeycloakInstance, initKeycloak } from '@/services/keycloak/keycloak';
import { getRuntimeConfig } from '@/config/runtimeConfig';

const AuthContext = createContext();

const resolveDisplayName = (keycloakInstance) => {
    const token = keycloakInstance?.tokenParsed;

    return (
        token?.name ||
        token?.preferred_username ||
        [token?.given_name, token?.family_name].filter(Boolean).join(' ') ||
        ''
    );
};

const resolveRoles = (keycloakInstance) => {
    const token = keycloakInstance?.tokenParsed;
    if (!token) {
        return [];
    }

    const realmRoles = token.realm_access?.roles || [];
    const resourceRoles = Object.values(token.resource_access || {}).flatMap(
        (resource) => resource?.roles || []
    );

    return Array.from(new Set([...realmRoles, ...resourceRoles]));
};

const loadRuntimeConfig = async () => {
    if (typeof window === 'undefined') {
        return getRuntimeConfig();
    }

    if (window.MAASAI_CONFIG) {
        return getRuntimeConfig();
    }

    const existingScript = document.querySelector('script[data-maasai-config="true"]');
    if (existingScript) {
        await new Promise((resolve) => {
            existingScript.addEventListener('load', resolve, { once: true });
            existingScript.addEventListener('error', resolve, { once: true });
        });
        return getRuntimeConfig();
    }

    await new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = '/config.js';
        script.async = true;
        script.dataset.maasaiConfig = 'true';
        script.addEventListener('load', resolve, { once: true });
        script.addEventListener('error', resolve, { once: true });
        document.head.appendChild(script);
    });

    return getRuntimeConfig();
};

export const AuthProvider = ({ children }) => {
    const [config, setConfig] = useState(getRuntimeConfig());
    const [keycloak, setKeycloak] = useState(null);
    const [authenticated, setAuthenticated] = useState(false);
    const [isInitialized, setIsInitialized] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [userName, setUserName] = useState('');
    const [roles, setRoles] = useState([]);

    useEffect(() => {
        let cancelled = false;

        const initAuth = async () => {
            const runtimeConfig = await loadRuntimeConfig();
            if (cancelled) {
                return;
            }

            setConfig(runtimeConfig);

            if (!runtimeConfig.keycloak.enabled) {
                setAuthenticated(false);
                setKeycloak(null);
                setUserName('');
                setIsInitialized(true);
                setIsLoading(false);
                return;
            }

            const keycloakInstance = getKeycloakInstance(runtimeConfig.keycloak);
            if (!keycloakInstance) {
                console.warn(
                    '[AuthContext] Keycloak instance could not be created. ' +
                    'Check `window.MAASAI_CONFIG.keycloak` in /public/config.js.'
                );
                setUserName('');
                setIsInitialized(true);
                setIsLoading(false);
                return;
            }

            setIsLoading(true);

            // eslint-disable-next-line no-console
            console.info('[AuthContext] Initializing Keycloak with', {
                realmUrl: runtimeConfig.keycloak.realmUrl,
                clientId: runtimeConfig.keycloak.clientId,
                onLoad: runtimeConfig.keycloak.onLoad || 'check-sso'
            });

            initKeycloak({
                onLoad: runtimeConfig.keycloak.onLoad || 'check-sso',
                checkLoginIframe: false,
                pkceMethod: 'S256'
            })
                .then((nextAuthenticated) => {
                    if (cancelled) {
                        return;
                    }

                    setKeycloak(keycloakInstance);
                    setAuthenticated(Boolean(nextAuthenticated));
                    setUserName(nextAuthenticated ? resolveDisplayName(keycloakInstance) : '');
                    setRoles(nextAuthenticated ? resolveRoles(keycloakInstance) : []);

                    if (nextAuthenticated && keycloakInstance) {
                        keycloakInstance.onTokenExpired = () => {
                            keycloakInstance.updateToken(30).catch((error) => {
                                console.warn('[AuthContext] Token refresh failed', error);
                                setAuthenticated(false);
                                setUserName('');
                            });
                        };
                    }
                })
                .catch((error) => {
                    if (!cancelled) {
                        console.error('[AuthContext] Error initializing Keycloak', error);
                        setAuthenticated(false);
                        setKeycloak(null);
                        setUserName('');
                        setRoles([]);
                    }
                })
                .finally(() => {
                    if (!cancelled) {
                        setIsInitialized(true);
                        setIsLoading(false);
                    }
                });
        };

        initAuth();

        return () => {
            cancelled = true;
        };
    }, []);

    const login = async () => {
        if (!keycloak) {
            console.warn('AuthContext.login called before Keycloak is ready');
            return;
        }

        await keycloak.login({
            redirectUri: window.location.href
        });
    };

    const logout = async () => {
        if (!keycloak) {
            console.warn('AuthContext.logout called before Keycloak is ready');
            return;
        }

        await keycloak.logout({
            redirectUri: window.location.origin
        });
        setAuthenticated(false);
        setUserName('');
        setRoles([]);
    };

    const hasRole = (role) => {
        if (!authenticated) return false;
        if (Array.isArray(role)) {
            return role.some((r) => roles.includes(r));
        }
        return roles.includes(role);
    };

    const value = {
        authenticated,
        isInitialized,
        isLoading,
        keycloak,
        config,
        userName,
        roles,
        hasRole,
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
