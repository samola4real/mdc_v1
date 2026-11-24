// Public browser runtime configuration only. Never place lifecycle tokens or
// other secrets here. Stage 1 MDC uses the local same-origin API.
window.MAASAI_CONFIG = {
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
