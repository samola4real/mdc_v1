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
