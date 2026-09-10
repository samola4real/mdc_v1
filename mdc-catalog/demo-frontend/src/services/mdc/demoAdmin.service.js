import { demoPath, get, post } from './client';

export const getDemoBackendStatus = (options) => (
    get(demoPath('/service-discovery/backend-status'), options)
);

export const runFusekiSmokeTest = (options) => (
    get(demoPath('/service-discovery/fuseki-smoke-test'), options)
);

export const regenerateRdf = (options) => (
    post(demoPath('/service-discovery/regenerate-rdf'), {}, options)
);

export const reloadFuseki = (options) => (
    post(demoPath('/service-discovery/reload-fuseki'), {}, options)
);

export const getProviderDemoState = (options) => (
    get(demoPath('/provider-publication/state'), options)
);

export const previewProviderPublication = (payload, options) => (
    post(demoPath('/provider-publication/preview'), payload, options)
);

export const simulateProviderUpdate = (payload, options) => (
    post(demoPath('/provider-publication/simulate-update'), payload, options)
);
