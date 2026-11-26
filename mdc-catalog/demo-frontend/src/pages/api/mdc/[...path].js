import { createRemoteJWKSet, jwtVerify } from 'jose';
import { getDefaultRuntimeConfig } from '../../../config/runtimeConfig.js';
import { normalizeDemoRoles } from '../../../components/mdc/demoAuth.js';
import { isDisposableMdcId, isDisposableOfferingId } from '../../../services/mdc/stage1bScope.js';

const preview = 'https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app';
const { realmUrl: issuer, clientId } = getDefaultRuntimeConfig().keycloak;
const issuerKeys = createRemoteJWKSet(new URL(issuer + '/protocol/openid-connect/certs'), { timeoutDuration: 5000 });
const userInfoEndpoint = new URL(issuer + '/protocol/openid-connect/userinfo');
const providerRoles = ['provider', 'admin'];
const demoRoles = ['provider', 'consumer', 'admin'];
const idSegment = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,511}$/;

const canonicalRoutes = {
    health: { methods: ['GET'], roles: demoRoles },
    'catalog/filters': { methods: ['GET'], roles: demoRoles },
    'service-discovery/search': { methods: ['POST'], roles: ['consumer', 'admin'] },
    'provider-publication/validation': { methods: ['POST'], roles: providerRoles },
    'provider-publication': { methods: ['POST'], roles: providerRoles, write: true }
};
const lifecycleMethods = {
    provider: ['GET', 'PATCH', 'DELETE'],
    offering: ['GET', 'PATCH', 'DELETE'],
    offerings: ['GET', 'POST']
};

export const resolveEndpoint = (segments, method) => {
    if (!Array.isArray(segments) || !segments.every((part) => typeof part === 'string' && idSegment.test(part))) return null;
    const path = segments.join('/');
    if (Object.hasOwn(canonicalRoutes, path)) return { ...canonicalRoutes[path], path };
    const [collection, id, nested] = segments;
    if (!id || segments.length > 3) return null;

    let resource;
    if (collection === 'providers' && nested === 'offerings') resource = 'offerings';
    else if (collection === 'providers' && !nested) resource = 'provider';
    else if (collection === 'offerings' && !nested) resource = 'offering';
    else return null;

    const roles = resource === 'provider' && method === 'DELETE' ? ['admin'] : providerRoles;
    return { path, id, resource, methods: lifecycleMethods[resource], roles, write: method !== 'GET' };
};

export const allowsDisposableWrite = (route, body) => {
    if (route.path === 'provider-publication') {
        return isDisposableMdcId(body?.provider_id) && Array.isArray(body.offerings)
            && body.offerings.length > 0
            && body.offerings.every((offering) => isDisposableOfferingId(offering?.offering_id, body.provider_id));
    }
    if (route.resource === 'offerings') return isDisposableOfferingId(body?.offering_id, route.id);
    return route.resource === 'offering' ? isDisposableOfferingId(route.id) : isDisposableMdcId(route.id);
};

const confirmKeycloakSession = async (token, subject) => {
    try {
        const response = await fetch(userInfoEndpoint, {
            headers: { Accept: 'application/json', Authorization: 'Bearer ' + token },
            cache: 'no-store',
            redirect: 'error',
            signal: AbortSignal.timeout(5000)
        });
        if (response.status === 401 || response.status === 403) return false;
        if (!response.ok) throw new Error('UserInfo request failed.');
        const identity = await response.json();
        return identity?.sub === subject;
    } catch {
        throw Object.assign(new Error('The Keycloak session check is unavailable.'), { code: 'ERR_KEYCLOAK_USERINFO' });
    }
};

export const verifyAccessRoles = async (token, audience, roleSource, keys = issuerKeys) => {
    const { payload } = await jwtVerify(token, keys, {
        algorithms: ['RS256'],
        issuer,
        audience: audience || undefined,
        requiredClaims: ['exp', 'sub', 'azp', 'typ']
    });
    if (payload.azp !== clientId || payload.typ !== 'Bearer' || typeof payload.sub !== 'string' || !payload.sub) {
        return [];
    }
    // The loopback-only session mode uses the pinned issuer to confirm the existing client session.
    if (!audience && !(await confirmKeycloakSession(token, payload.sub))) {
        throw new Error('The Keycloak session could not be verified.');
    }
    const claims = {
        realm: payload.realm_access?.roles,
        client: payload.resource_access?.[clientId]?.roles
    };
    const sources = roleSource ? [claims[roleSource]] : [claims.realm, claims.client];
    const signedRoles = sources.flatMap((roles) => Array.isArray(roles) ? roles : [])
        .filter((role) => typeof role === 'string');
    return normalizeDemoRoles(signedRoles).filter((role) => demoRoles.includes(role));
};

const fail = (res, status, code, message) => res.status(status).json({
    contract_version: '1.0',
    error: { code, message }
});

const localRequest = (req) => {
    const host = req.headers.host || '';
    return ['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(req.socket.remoteAddress)
        && /^(localhost|127\.0\.0\.1|\[::1\])(?::[0-9]{1,5})?$/i.test(host)
        && (!req.headers.origin || req.headers.origin === 'http://' + host);
};

export default async function stage1bMdc(req, res) {
    res.setHeader('Cache-Control', 'no-store');
    if (!localRequest(req)) return fail(res, 403, 'local_mdc_only', 'This demo API is available on loopback only.');

    const endpoint = resolveEndpoint(req.query.path, req.method);
    if (!endpoint) return fail(res, 404, 'mdc_route_not_found', 'This MDC route is unavailable.');
    if (!endpoint.methods.includes(req.method)) {
        res.setHeader('Allow', endpoint.methods.join(', '));
        return fail(res, 405, 'method_not_allowed', 'This method is unavailable for this MDC route.');
    }

    const auth = req.headers.authorization;
    const match = typeof auth === 'string' && auth.length <= 16384
        && /^Bearer ([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)$/.exec(auth);
    if (!match) return fail(res, 401, 'keycloak_token_required', 'Sign in with MaaSAI Keycloak to continue.');

    const audience = process.env.MDC_KEYCLOAK_AUDIENCE?.trim();
    const roleSource = process.env.MDC_KEYCLOAK_ROLE_SOURCE?.trim();
    if ((audience || roleSource) && !['client', 'realm'].includes(roleSource)) {
        return fail(res, 503, 'identity_configuration_required', 'Set a supported Keycloak role source for the configured identity policy.');
    }
    let roles;
    try {
        roles = await verifyAccessRoles(match[1], audience, roleSource);
    } catch (error) {
        if (['ERR_JWKS_TIMEOUT', 'ERR_JWKS_INVALID', 'ERR_KEYCLOAK_USERINFO'].includes(error?.code) || error instanceof TypeError) {
            return fail(res, 503, 'keycloak_unavailable', 'The local server could not verify the Keycloak session.');
        }
        return fail(res, 401, 'invalid_keycloak_token', 'Sign in again with MaaSAI Keycloak.');
    }
    if (!endpoint.roles.some((role) => roles.includes(role))) {
        return fail(res, 403, 'mdc_role_forbidden', 'Your verified Keycloak role cannot use this MDC operation.');
    }
    if (endpoint.write && !allowsDisposableWrite(endpoint, req.body)) {
        return fail(res, 403, 'disposable_identity_required', 'Writes require Stage 1B disposable provider and offering IDs.');
    }

    const bypass = process.env.MDC_VERCEL_PROTECTION_BYPASS;
    if (!bypass) return fail(res, 503, 'preview_access_unconfigured', 'The local server needs approved Vercel Preview access.');
    const conditional = req.headers['if-match'];
    const alternate = req.headers['x-mdc-if-match'];
    if ((conditional && alternate && conditional !== alternate)
        || [conditional, alternate].some((value) => value && typeof value !== 'string')) {
        return fail(res, 400, 'invalid_concurrency_precondition', 'Provide one current strong ETag.');
    }
    const etag = conditional || alternate;
    const headers = { Accept: 'application/json', 'x-vercel-protection-bypass': bypass };
    if (req.method === 'GET' && ['provider', 'offering'].includes(endpoint.resource)) {
        // Preview compression weakens the lifecycle ETag needed for a conditional write.
        headers['Accept-Encoding'] = 'identity';
    }
    if (etag && ['PATCH', 'DELETE'].includes(req.method)) headers['X-MDC-If-Match'] = etag;
    const sendsBody = ['POST', 'PATCH'].includes(req.method);
    if (sendsBody) {
        if (!req.body || typeof req.body !== 'object' || Array.isArray(req.body)) {
            return fail(res, 400, 'invalid_request_body', 'Send a JSON object.');
        }
        headers['Content-Type'] = 'application/json';
    }
    try {
        const upstream = await fetch(preview + '/api/' + endpoint.path, {
            method: req.method, headers, redirect: 'error', signal: AbortSignal.timeout(12000),
            body: sendsBody ? JSON.stringify(req.body) : undefined
        });
        const data = await upstream.json().catch(() => null);
        if (data?.contract_version !== '1.0') {
            return fail(res, upstream.ok ? 502 : upstream.status, 'preview_response_unavailable',
                'The protected Preview did not return an MDC response. Check local Preview access.');
        }
        const responseTag = upstream.headers.get('etag');
        if (responseTag) res.setHeader('ETag', responseTag);
        res.statusCode = upstream.status;
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify(data));
    } catch {
        return fail(res, 502, 'preview_connection_failed', 'The protected Preview did not respond. Check the resource before retrying a write.');
    }
}
