/**
 * Single source of truth for route access control.
 *
 * Each entry maps a Next.js pathname to its access requirement:
 *   - 'public'        → accessible without authentication
 *   - 'authenticated' → requires an active Keycloak session
 *   - ['role1', ...]  → requires authentication AND at least one of those Keycloak realm roles
 *
 * Both `_app.js` (route protection) and `AppMenu.js` (visibility) read from
 * this object, so adding a new route in one place is enough.
 */
export const ROUTE_ACCESS = {
    '/': 'public',
    '/404': 'public',
    '/home/Contact': 'public',
    '/home/Help': 'public',
    '/home/Brand': 'public',
    '/home/AccessDenied': 'public',
    '/home/ErrorPage': 'public',
    '/demo': 'public',
    '/demo/provider': 'authenticated',
    '/demo/consumer-search': 'authenticated',
    '/demo/admin-audit': 'authenticated',

    '/home/EmptyPage': 'authenticated',
    '/workspace/charts': 'authenticated',
    '/workspace/crud': 'authenticated',
    '/workspace/agents': 'authenticated',
    '/workspace/monitor': 'authenticated',
    '/workspace/scheduler': 'authenticated',
    '/workspace/analytics': 'authenticated',
    '/workspace/designer': 'authenticated'
};

const DEFAULT_ACCESS = 'authenticated';

export const getRouteAccess = (pathname = '') => {
    if (Object.prototype.hasOwnProperty.call(ROUTE_ACCESS, pathname)) {
        return ROUTE_ACCESS[pathname];
    }
    return DEFAULT_ACCESS;
};

export const isPublicRoute = (pathname = '') => {
    return getRouteAccess(pathname) === 'public';
};

export const requiresAuth = (pathname = '') => {
    return getRouteAccess(pathname) !== 'public';
};

export const requiresRoles = (pathname = '') => {
    const access = getRouteAccess(pathname);
    return Array.isArray(access) ? access : null;
};

/**
 * Returns true if the given user (with the supplied Keycloak roles) can
 * access the route. Used by both the menu and the central route guard.
 */
export const canAccessRoute = (pathname, { authenticated, roles = [] } = {}) => {
    const access = getRouteAccess(pathname);

    if (access === 'public') {
        return true;
    }

    if (!authenticated) {
        return false;
    }

    if (Array.isArray(access)) {
        return access.some((role) => roles.includes(role));
    }

    return true;
};
