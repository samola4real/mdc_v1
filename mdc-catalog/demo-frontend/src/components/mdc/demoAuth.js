import { useEffect, useState } from 'react';

export const DEMO_SELECTED_ROLE_STORAGE_KEY = 'mdc_demo_selected_role';
export const DEMO_SELECTED_ROLE_CHANGE_EVENT = 'mdc-demo-selected-role-change';

const DEMO_ROLE_VALUES = ['provider', 'consumer', 'admin'];

const ROLE_ALIASES = {
    provider: 'provider',
    mdc_provider: 'provider',
    maas_provider: 'provider',
    consumer: 'consumer',
    mdc_consumer: 'consumer',
    maas_consumer: 'consumer',
    admin: 'admin',
    mdc_admin: 'admin',
    maas_admin: 'admin'
};

export const normalizeDemoRoles = (roles = []) => {
    const normalized = roles
        .map((role) => ROLE_ALIASES[String(role).toLowerCase()])
        .filter(Boolean);

    return Array.from(new Set(normalized));
};

export const getDemoRolesFromKeycloak = (keycloak, fallbackRoles = []) => {
    const token = keycloak?.tokenParsed;
    const clientId = keycloak?.clientId || keycloak?.client_id;
    const realmRoles = token?.realm_access?.roles || [];
    const resourceAccess = token?.resource_access || {};
    const directClientRoles = clientId ? resourceAccess[clientId]?.roles || [] : [];
    const allResourceRoles = Object.values(resourceAccess).flatMap((resource) => resource?.roles || []);

    return normalizeDemoRoles([
        ...fallbackRoles,
        ...realmRoles,
        ...directClientRoles,
        ...allResourceRoles
    ]);
};

export const getPrimaryDemoRole = (demoRoles = []) => {
    if (demoRoles.includes('admin')) return 'admin';
    if (demoRoles.includes('provider')) return 'provider';
    if (demoRoles.includes('consumer')) return 'consumer';
    return null;
};

export const canAccessDemoRole = (demoRoles = [], allowedRoles = []) => (
    allowedRoles.some((role) => demoRoles.includes(role))
);

export const isDemoRoleValue = (role) => DEMO_ROLE_VALUES.includes(role);

export const getStoredDemoRole = () => {
    if (typeof window === 'undefined') {
        return null;
    }

    const role = window.sessionStorage.getItem(DEMO_SELECTED_ROLE_STORAGE_KEY);
    return isDemoRoleValue(role) ? role : null;
};

export const setStoredDemoRole = (role) => {
    if (typeof window === 'undefined' || !isDemoRoleValue(role)) {
        return;
    }

    window.sessionStorage.setItem(DEMO_SELECTED_ROLE_STORAGE_KEY, role);
    window.dispatchEvent(new Event(DEMO_SELECTED_ROLE_CHANGE_EVENT));
};

export const clearStoredDemoRole = () => {
    if (typeof window === 'undefined') {
        return;
    }

    window.sessionStorage.removeItem(DEMO_SELECTED_ROLE_STORAGE_KEY);
    window.dispatchEvent(new Event(DEMO_SELECTED_ROLE_CHANGE_EVENT));
};

export const useSelectedDemoRole = () => {
    const [selectedRole, setSelectedRole] = useState(null);

    useEffect(() => {
        const updateSelectedRole = () => setSelectedRole(getStoredDemoRole());

        updateSelectedRole();
        window.addEventListener(DEMO_SELECTED_ROLE_CHANGE_EVENT, updateSelectedRole);
        window.addEventListener('storage', updateSelectedRole);

        return () => {
            window.removeEventListener(DEMO_SELECTED_ROLE_CHANGE_EVENT, updateSelectedRole);
            window.removeEventListener('storage', updateSelectedRole);
        };
    }, []);

    return selectedRole;
};

export const roleLabel = (role) => {
    if (role === 'admin') return 'Admin';
    if (role === 'provider') return 'Provider';
    if (role === 'consumer') return 'Consumer';
    return 'MDC demo user';
};
