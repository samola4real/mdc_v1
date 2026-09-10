// Public browser runtime configuration only. Never place lifecycle tokens or
// other secrets here. Override baseUrl with the deployed HTTPS MDC API URL.
window.MAASAI_CONFIG = {
    keycloak: {
        enabled: true,
        realmUrl: 'https://login.maasai-srv.cigip.upv.es/realms/MAASAI',
        clientId: 'myClient',
        onLoad: 'check-sso'
    },
    mdcApi: {
        baseUrl: 'http://localhost:8000',
        sharedApiPrefix: '/api',
        demoApiPrefix: '/api/demo'
    }
};
