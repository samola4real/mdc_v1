# MDC Demo Frontend

This Next.js application is an illustrative frontend for the MaaS Dynamic Catalogue (MDC). It demonstrates how provider, consumer, and administrator interactions could look before full Marketplace integration. It is **not the real Cloud MaaS Marketplace (CMM)**.

## Demo roles and API boundaries

- Consumer search uses the current public MDC API: `GET /api/catalog/filters` and `POST /api/service-discovery/search`.
- Shared health status uses `GET /api/health`.
- Provider registration/update and administrator controls use `/api/demo/...` endpoints and demo persistence. These endpoints may be disabled in normal production environments.
- Provider, consumer, and admin role guards are client-side presentation controls. Backend authorization remains a separate responsibility.

The browser does not call trusted provider lifecycle write APIs. Those APIs require a server-to-server service-token, actor, and ETag boundary that must eventually sit behind the Marketplace/CMM or another backend-for-frontend. Never place lifecycle tokens or other secrets in source, `NEXT_PUBLIC_*`, `public/config.js`, `window.MAASAI_CONFIG`, local storage, or session storage.

## Local development

The Docker build uses Node.js 20.18.0. Use Node.js 20.18 or another compatible Node 20 release and an npm version that supports the committed lockfile v3.

```bash
npm ci
npm run dev
```

The frontend runs at `http://localhost:3000`. By local convention, its default MDC API is `http://localhost:8000`.

Validation and production-style startup commands are:

```bash
npm run lint
npm run build
npm run start
```

## Browser runtime configuration

The application loads `/config.js`, which defines `window.MAASAI_CONFIG`. Override it for each deployed environment; browser runtime configuration is public and must never contain credentials.

```js
window.MAASAI_CONFIG = {
    keycloak: {
        enabled: true,
        realmUrl: 'https://identity.example.org/realms/example',
        clientId: 'mdc-demo-frontend',
        onLoad: 'check-sso'
    },
    mdcApi: {
        baseUrl: 'https://mdc-api.example.org',
        sharedApiPrefix: '/api',
        demoApiPrefix: '/api/demo'
    }
};
```

Deployed browser-to-backend traffic should use an appropriate HTTPS endpoint. The backend CORS/origin policy must permit the deployed frontend origin. The accepted current MDC production deployment normally has the demo API disabled, so provider/admin demo actions require a deliberately demo-enabled backend environment.

## Repository and release boundary

GitHub is the controlled development source after the sanitized snapshot import. GitLab remains the historical and official release repository; approved releases use a fresh checkout and reviewed file synchronization rather than importing GitLab history or retaining a GitLab remote here.

- [Sanitized snapshot provenance](../docs/Demo_Frontend/00_frontend_sanitized_snapshot_import_provenance.md)
- [GitHub-to-GitLab release mapping](../docs/Demo_Frontend/01_frontend_github_to_gitlab_release_mapping.md)
- [Comprehensive MDC implementation report and user manual](../docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md)
