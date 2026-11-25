// The local Stage 1 MDC calls use a same-origin server route.
const defaultConfig = {
    keycloak: {
        enabled: true,
        realmUrl: 'https://login.maasai-srv.cigip.upv.es/realms/MAASAI',
        clientId: 'myClient',
        onLoad: 'check-sso'
    },
    mdcApi: {
        baseUrl: '',
        sharedApiPrefix: '/api/mdc'
    }
};

const mergeConfig = (baseConfig, overrideConfig) => {
    return {
        ...baseConfig,
        ...overrideConfig,
        keycloak: {
            ...baseConfig.keycloak,
            ...(overrideConfig?.keycloak || {})
        },
        mdcApi: {
            ...baseConfig.mdcApi,
            ...(overrideConfig?.mdcApi || {})
        }
    };
};

export const getRuntimeConfig = () => {
    if (typeof window === 'undefined') {
        return defaultConfig;
    }

    return mergeConfig(defaultConfig, window.MAASAI_CONFIG || {});
};

export const getDefaultRuntimeConfig = () => defaultConfig;

export const getMdcApiConfig = () => getRuntimeConfig().mdcApi;

export const getMdcApiBaseUrl = () => getMdcApiConfig().baseUrl;

export const getMdcSharedApiPrefix = () => getMdcApiConfig().sharedApiPrefix;
