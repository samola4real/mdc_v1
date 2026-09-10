import Keycloak from 'keycloak-js';

let keycloakInstance = null;
let keycloakSignature = null;
let keycloakInitPromise = null;

const normalizeKeycloakConfig = (keycloakConfig) => {
    const rawRealmUrl = keycloakConfig.realmUrl || keycloakConfig.url;

    if (rawRealmUrl && rawRealmUrl.includes('/realms/')) {
        const parsedUrl = new URL(rawRealmUrl);
        const realmMatch = parsedUrl.pathname.match(/^(.*)\/realms\/([^/]+)\/?$/);

        if (realmMatch) {
            const [, basePath, realm] = realmMatch;
            const normalizedBasePath = basePath || '';

            return {
                url: `${parsedUrl.origin}${normalizedBasePath}`,
                realm,
                clientId: keycloakConfig.clientId
            };
        }
    }

    return {
        url: keycloakConfig.url,
        realm: keycloakConfig.realm,
        clientId: keycloakConfig.clientId
    };
};

export const getKeycloakInstance = (keycloakConfig) => {
    if (typeof window === 'undefined' || !keycloakConfig) {
        return null;
    }

    const normalizedConfig = normalizeKeycloakConfig(keycloakConfig);

    if (!normalizedConfig.url || !normalizedConfig.realm || !normalizedConfig.clientId) {
        console.error(
            '[keycloak] Missing required config field. Got:',
            normalizedConfig
        );
        return null;
    }

    const nextSignature = JSON.stringify(normalizedConfig);

    if (!keycloakInstance || keycloakSignature !== nextSignature) {
        keycloakInstance = new Keycloak(normalizedConfig);
        keycloakSignature = nextSignature;
        keycloakInitPromise = null;
    }

    return keycloakInstance;
};

/**
 * Initializes the Keycloak instance exactly once per page load. Calling this
 * multiple times (e.g. from React Strict Mode's double-mount) returns the
 * same promise instead of triggering a second `init()`, which keycloak-js
 * rejects with "A 'Keycloak' instance can only be initialized once".
 */
export const initKeycloak = (initOptions = {}) => {
    if (!keycloakInstance) {
        return Promise.reject(
            new Error('initKeycloak called before getKeycloakInstance')
        );
    }

    if (keycloakInstance.authenticated !== undefined) {
        return Promise.resolve(Boolean(keycloakInstance.authenticated));
    }

    if (!keycloakInitPromise) {
        keycloakInitPromise = keycloakInstance.init(initOptions);
    }

    return keycloakInitPromise;
};
