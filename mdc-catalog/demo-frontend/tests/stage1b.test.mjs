import assert from 'node:assert/strict';
import test from 'node:test';
import { exportJWK, generateKeyPair, SignJWT } from 'jose';
import route, { allowsDisposableWrite, resolveEndpoint, verifyAccessRoles } from '../src/pages/api/mdc/[...path].js';
import { exactOffering, loadManagementSnapshot, strongEtag } from '../src/components/mdc/providerManagementFlow.js';
import { readBackRegistration } from '../src/components/mdc/providerRegistrationFlow.js';
import { formatSuitability } from '../src/components/mdc/searchResultFormatters.js';
import {
    buildProviderPatches, buildProviderPreviewPayload, emptyProviderForm, hydrateProviderForm
} from '../src/components/mdc/providerPayloadBuilder.js';

const providerId = 'mdc_stage1b_test';
const offeringId = providerId + '_primary';
const issuer = 'https://login.maasai-srv.cigip.upv.es/realms/MAASAI';
const audience = 'offline-stage1b-test';
const provider = {
    provider_id: providerId, provider_name: 'Test provider', country: 'Finland',
    custom_provider_fields: { description: 'Original note', external_reference: 'retained' },
    certifications: []
};
const offering = {
    offering_id: offeringId, offering_name: 'Test gears', provider_id: providerId,
    part_family: 'gear', service_category: 'precision_gears', support_status: 'confirmed',
    supported_part_types: [{ part_type: 'spur_gear', support_status: 'confirmed', source_type: 'provider_confirmed', confidence: 'declared' }],
    family_capabilities: {
        module: { min: 1, max: 4, source_type: 'provider_confirmed', confidence: 'declared', source_note: 'keep' },
        number_of_teeth: { max: 70 }
    },
    part_type_capabilities: { spur_gear: { face_width_mm: { max: 15 } } },
    generic_capabilities: { weight_kg: { max: 200 }, batch_size: { min: 2, max: 40 } },
    custom_offering_fields: { comment: 'remove', opaque: { facts: [1] }, other: 'keep' },
    custom_capability_fields: {}
};

test('discovery labels distinguish eligibility from unmet or unconfirmed requirements', () => {
    assert.equal(formatSuitability('full_match'), 'Eligible');
    assert.equal(formatSuitability('partial_match'), 'Requirements unmet');
    assert.equal(formatSuitability('unmatched'), 'Requirements unmet');
    assert.equal(formatSuitability('unknown_match'), 'Evidence incomplete');
});

test('registration uses the canonical envelope and typed evidence', () => {
    const body = buildProviderPreviewPayload({
        ...emptyProviderForm(), providerId, providerName: provider.provider_name, country: provider.country,
        description: 'Provider note', offeringId, offeringName: offering.offering_name,
        partFamily: 'gear', serviceCategory: 'precision_gears', partTypes: ['spur_gear'],
        materials: ['steel'], availableGrades: '42CrMo4', processes: ['hobbing'], weightMaxKg: 20,
        customOfferingFields: [{ name: 'custom_note', value: 'value' }]
    });
    const [created] = body.offerings;
    assert.equal(body.contract_version, '1.0');
    assert.equal(body.action, undefined);
    assert.equal(body.custom_provider_fields.description, 'Provider note');
    assert.equal(created.offering_id, offeringId);
    assert.deepEqual(created.supported_part_types, offering.supported_part_types);
    assert.deepEqual(created.generic_capabilities.materials[0].available_grades, ['42CrMo4']);
    assert.equal(created.generic_capabilities.processes[0].process, 'hobbing');
    assert.equal(created.custom_offering_fields.custom_note, 'value');
    assert.equal(created.generic_capabilities.weight_kg.max, 20);
});

test('unchanged state creates no PATCH and provider fields are independent', () => {
    const form = hydrateProviderForm(provider, offering);
    assert.deepEqual(buildProviderPatches(form, provider, offering), { provider: {}, offering: {} });
    const changes = buildProviderPatches({ ...form, providerName: 'Updated', description: '' }, provider, offering);
    assert.deepEqual(changes, { provider: { provider_name: 'Updated', custom_provider_fields: { external_reference: 'retained' } }, offering: {} });
});

test('a selected map replacement keeps untouched leaves, excludes identity, and removes a cleared leaf', () => {
    const form = hydrateProviderForm(provider, offering);
    const { offering: changed } = buildProviderPatches({ ...form, moduleMin: null, offeringName: 'Edited' }, provider, offering);
    assert.deepEqual(Object.keys(changed), ['offering_name', 'family_capabilities']);
    assert.deepEqual(changed.family_capabilities.module, {
        max: 4, source_type: 'provider_confirmed', confidence: 'declared', source_note: 'keep'
    });
    assert.deepEqual(changed.family_capabilities.number_of_teeth, offering.family_capabilities.number_of_teeth);
});

test('removing a custom field preserves opaque and sibling values', () => {
    const initial = hydrateProviderForm(provider, offering);
    const { offering: changed } = buildProviderPatches({
        ...initial, customOfferingFields: initial.customOfferingFields.filter((field) => field.name !== 'comment')
    }, provider, offering);
    assert.deepEqual(changed.custom_offering_fields, { opaque: { facts: [1] }, other: 'keep' });
});

test('server route and disposable scope deny legacy paths, traversal, mismatched IDs, and real writes', () => {
    assert.equal(resolveEndpoint(['demo', 'provider-publication', 'state'], 'POST'), null);
    assert.equal(resolveEndpoint(['providers', '../real'], 'PATCH'), null);
    assert.equal(resolveEndpoint(['providers', providerId, 'offerings', 'bad'], 'POST'), null);
    assert.equal(allowsDisposableWrite(resolveEndpoint(['providers', 'tasowheel'], 'PATCH'), {}), false);
    assert.equal(allowsDisposableWrite(resolveEndpoint(['offerings', 'precipart_precision_gears'], 'DELETE'), {}), false);
    assert.equal(allowsDisposableWrite(resolveEndpoint(['providers', providerId, 'offerings'], 'POST'), { offering_id: 'mdc_stage1b_other_thing' }), false);
    assert.equal(allowsDisposableWrite(resolveEndpoint(['provider-publication'], 'POST'), {
        provider_id: providerId, offerings: [{ offering_id: offeringId }]
    }), true);
});

const { privateKey, publicKey } = await generateKeyPair('RS256');
const kid = 'stage1b-offline-test';
const fixture = (claims = {}, options = {}) => {
    const token = new SignJWT({
        azp: 'myClient', typ: 'Bearer',
        resource_access: { myClient: { roles: ['mdc_provider'] }, unrelated: { roles: ['admin'] } },
        ...claims
    }).setProtectedHeader({ alg: 'RS256', kid })
        .setIssuer(options.issuer || issuer).setSubject('offline-user').setExpirationTime(options.exp || '10m');
    if (options.audience !== null) token.setAudience(options.audience || audience);
    return token.sign(options.signer || privateKey);
};

test('offline signed fixtures enforce issuer, audience, expiry, signature, and authorized party', async () => {
    assert.deepEqual(await verifyAccessRoles(await fixture(), audience, 'client', publicKey), ['provider']);
    assert.deepEqual(await verifyAccessRoles(await fixture({ azp: 'unrelated' }), audience, 'client', publicKey), []);
    await assert.rejects(verifyAccessRoles(await fixture({}, { issuer: issuer + '/other' }), audience, 'client', publicKey));
    await assert.rejects(verifyAccessRoles(await fixture({}, { audience: 'unrelated' }), audience, 'client', publicKey));
    await assert.rejects(verifyAccessRoles(await fixture({}, { exp: 1 }), audience, 'client', publicKey));
    const other = await generateKeyPair('RS256');
    await assert.rejects(verifyAccessRoles(await fixture({}, { signer: other.privateKey }), audience, 'client', publicKey));
});

test('offline loopback session requires matching issuer UserInfo and uses only signed demo roles', async (t) => {
    const token = await fixture({ realm_access: { roles: ['consumer', 'ordinary-realm-role'] } }, { audience: null });
    const userInfo = t.mock.method(globalThis, 'fetch', async (url, options) => {
        assert.equal(String(url), issuer + '/protocol/openid-connect/userinfo');
        assert.equal(options.headers.Authorization === 'Bearer ' + token, true);
        assert.equal(options.cache, 'no-store');
        assert.equal(options.redirect, 'error');
        return Response.json({ sub: 'offline-user', realm_access: { roles: ['admin'] } });
    });
    assert.deepEqual(await verifyAccessRoles(token, undefined, undefined, publicKey), ['consumer', 'provider']);
    assert.deepEqual(await verifyAccessRoles(token, undefined, 'client', publicKey), ['provider']);
    assert.deepEqual(await verifyAccessRoles(token, undefined, 'realm', publicKey), ['consumer']);
    await assert.rejects(verifyAccessRoles(token, audience, 'client', publicKey));
    assert.deepEqual(await verifyAccessRoles(await fixture({ azp: 'unrelated' }), undefined, undefined, publicKey), []);
    assert.deepEqual(await verifyAccessRoles(await fixture({ typ: 'ID' }), undefined, undefined, publicKey), []);
    await assert.rejects(verifyAccessRoles(await fixture({}, { exp: 1 }), undefined, undefined, publicKey));
    assert.equal(userInfo.mock.callCount(), 3);
});

const invoke = async ({ method, path, authorization, body, extraHeaders, remoteAddress = '127.0.0.1' }) => {
    const reply = { statusCode: 200, headers: {}, data: null };
    const res = {
        setHeader(key, value) { reply.headers[key] = value; },
        status(status) { reply.statusCode = status; return this; },
        json(data) { reply.data = data; },
        end(data) { reply.data = JSON.parse(data); },
        set statusCode(status) { reply.statusCode = status; }
    };
    await route({
        method, body, query: { path }, socket: { remoteAddress },
        headers: { host: 'localhost:3000', authorization, ...extraHeaders }
    }, res);
    return reply;
};

test('the API rejects anonymous writes, non-loopback access, and unsupported methods', async () => {
    const path = ['providers', providerId];
    assert.equal((await invoke({ method: 'PATCH', path })).statusCode, 401);
    assert.equal((await invoke({ method: 'PATCH', path, remoteAddress: '192.0.2.5' })).statusCode, 403);
    assert.equal((await invoke({ method: 'GET', path, extraHeaders: { origin: 'https://other.example' } })).statusCode, 403);
    assert.equal((await invoke({ method: 'PUT', path })).statusCode, 405);
});

test('offline transport preserves exact ETag and receipt, strips identity headers, and forbids Consumer writes', async (t) => {
    const jwk = { ...await exportJWK(publicKey), kid, alg: 'RS256' };
    const key = 'MDC_KEYCLOAK_AUDIENCE';
    const keys = [key, 'MDC_KEYCLOAK_ROLE_SOURCE', 'MDC_VERCEL_PROTECTION_BYPASS'];
    const previous = keys.map((name) => process.env[name]);
    t.after(() => keys.forEach((name, i) => {
        if (previous[i] === undefined) delete process.env[name];
        else process.env[name] = previous[i];
    }));
    process.env[key] = audience;
    process.env.MDC_KEYCLOAK_ROLE_SOURCE = 'client';
    process.env.MDC_VERCEL_PROTECTION_BYPASS = 'offline-fixture-only';
    const upstream = [];
    const tag = '"mdc-opaque-revision"';
    t.mock.method(globalThis, 'fetch', async (url, options) => {
        if (String(url) === issuer + '/protocol/openid-connect/certs') return Response.json({ keys: [jwk] });
        upstream.push({ url, options });
        return Response.json({ contract_version: '1.0', publication_id: 'offline-receipt', sync_status: 'pending',
            error: { code: 'catalogue_publication_incomplete' } }, { status: 503, headers: { ETag: tag } });
    });
    const path = ['providers', providerId];
    const consumer = await fixture({
        resource_access: { myClient: { roles: ['consumer'] }, unrelated: { roles: ['admin'] } },
        realm_access: { roles: ['admin'] }
    });
    assert.equal((await invoke({ method: 'PATCH', path, authorization: 'Bearer ' + consumer })).statusCode, 403);
    const authorization = 'Bearer ' + await fixture();
    assert.equal((await invoke({
        method: 'PATCH', path: ['providers', 'tasowheel'], body: {}, authorization
    })).statusCode, 403);
    assert.equal(upstream.length, 0);
    const reply = await invoke({ method: 'PATCH', path, body: { provider_name: 'Updated' }, authorization,
        extraHeaders: { 'if-match': tag, 'x-mdc-actor-id': 'browser-actor' } });
    assert.equal(reply.statusCode, 503);
    assert.equal(reply.headers.ETag, tag);
    assert.equal(reply.data.publication_id, 'offline-receipt');
    assert.equal(reply.data.sync_status, 'pending');
    const [{ url, options }] = upstream;
    assert.equal(url, 'https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app/api/providers/' + providerId);
    assert.equal(options.headers['X-MDC-If-Match'], tag);
    assert.equal(options.headers['x-vercel-protection-bypass'], 'offline-fixture-only');
    assert.equal(options.headers.Authorization, undefined);
    assert.equal(options.headers['x-mdc-actor-id'], undefined);
    assert.equal(options.redirect, 'error');
});

test('signed Consumer can read only the two exact lifecycle details and cannot use client roles for writes', async (t) => {
    const jwk = { ...await exportJWK(publicKey), kid, alg: 'RS256' };
    const config = { MDC_KEYCLOAK_AUDIENCE: audience, MDC_KEYCLOAK_ROLE_SOURCE: 'client', MDC_VERCEL_PROTECTION_BYPASS: 'offline-fixture-only' };
    const previous = Object.keys(config).map((key) => [key, process.env[key]]);
    t.after(() => previous.forEach(([key, value]) => {
        if (value === undefined) delete process.env[key];
        else process.env[key] = value;
    }));
    Object.assign(process.env, config);
    const requests = [];
    const etag = '"fixture-revision"';
    t.mock.method(globalThis, 'fetch', async (url, options) => {
        if (String(url) === issuer + '/protocol/openid-connect/certs') return Response.json({ keys: [jwk] });
        requests.push({ url: String(url), options });
        return Response.json({ contract_version: '1.0' }, { headers: { ETag: etag } });
    });
    const authorization = 'Bearer ' + await fixture({
        resource_access: { myClient: { roles: ['consumer'] }, unrelated: { roles: ['admin'] } },
        realm_access: { roles: ['admin'] }
    });
    const detailPaths = [['providers', providerId], ['offerings', offeringId]];
    for (const path of detailPaths) {
        assert.equal((await invoke({ method: 'GET', path, extraHeaders: { 'x-mdc-actor-role': 'admin' } })).statusCode, 401);
        const reply = await invoke({ method: 'GET', path, authorization });
        assert.equal(reply.statusCode, 200);
        assert.equal(reply.headers.ETag, etag);
        assert.equal(reply.headers['Cache-Control'], 'no-store');
        for (const method of ['PATCH', 'DELETE']) {
            const denied = await invoke({ method, path, authorization, body: {}, extraHeaders: { 'if-match': etag, 'x-mdc-actor-role': 'admin' } });
            assert.equal(denied.statusCode, 403);
            assert.equal(denied.data.error.code, 'mdc_role_forbidden');
        }
    }
    for (const [method, path] of [
        ['GET', ['providers', providerId, 'offerings']],
        ['POST', ['providers', providerId, 'offerings']],
        ['POST', ['provider-publication', 'validation']],
        ['POST', ['provider-publication']]
    ]) {
        assert.equal((await invoke({ method, path, authorization, body: {} })).statusCode, 403);
    }
    assert.deepEqual(requests.map(({ url }) => url), detailPaths.map((path) => (
        'https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app/api/' + path.join('/')
    )));
    for (const { options } of requests) {
        assert.equal(options.method, 'GET');
        assert.equal(options.headers['Accept-Encoding'], 'identity');
        assert.equal(options.headers.Authorization, undefined);
        assert.equal(options.headers['x-vercel-protection-bypass'], 'offline-fixture-only');
    }
});

test('only signed lenient discovery uses the new fixed Preview origin', async (t) => {
    const jwk = { ...await exportJWK(publicKey), kid, alg: 'RS256' };
    const config = { MDC_KEYCLOAK_AUDIENCE: audience, MDC_KEYCLOAK_ROLE_SOURCE: 'client', MDC_VERCEL_PROTECTION_BYPASS: 'offline-fixture-only' };
    const previous = Object.keys(config).map((key) => [key, process.env[key]]);
    t.after(() => previous.forEach(([key, value]) => {
        if (value === undefined) delete process.env[key];
        else process.env[key] = value;
    }));
    Object.assign(process.env, config);
    const requests = [];
    t.mock.method(globalThis, 'fetch', async (url, options) => {
        if (String(url) === issuer + '/protocol/openid-connect/certs') return Response.json({ keys: [jwk] });
        requests.push({ url: String(url), options });
        return Response.json({ contract_version: '1.0' });
    });
    const path = ['service-discovery', 'search'];
    const body = { match_policy: { discovery_mode: 'lenient' } };
    const consumer = 'Bearer ' + await fixture({ resource_access: { myClient: { roles: ['consumer'] } } });
    assert.equal((await invoke({ method: 'POST', path, body })).statusCode, 401);
    assert.equal((await invoke({ method: 'POST', path, body, authorization: 'Bearer ' + await fixture() })).statusCode, 403);
    assert.equal((await invoke({ method: 'POST', path, body, authorization: consumer })).statusCode, 200);
    assert.equal((await invoke({ method: 'POST', path, body: {}, authorization: consumer })).statusCode, 200);
    assert.deepEqual(requests.map(({ url }) => url), [
        'https://maasai-mdc-v1-ei6ijogqi-mdc19.vercel.app/api/service-discovery/search',
        'https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app/api/service-discovery/search'
    ]);
    for (const { options } of requests) {
        assert.equal(options.headers.Authorization, undefined);
        assert.equal(options.headers['x-vercel-protection-bypass'], 'offline-fixture-only');
        assert.equal(options.redirect, 'error');
    }
});

test('offline relay requires signed Admin for provider deletion and retains disposable scope for every role', async (t) => {
    const jwk = { ...await exportJWK(publicKey), kid, alg: 'RS256' };
    const config = { MDC_KEYCLOAK_AUDIENCE: audience, MDC_KEYCLOAK_ROLE_SOURCE: 'client', MDC_VERCEL_PROTECTION_BYPASS: 'offline-fixture-only' };
    const previous = Object.keys(config).map((key) => [key, process.env[key]]);
    t.after(() => previous.forEach(([key, value]) => {
        if (value === undefined) delete process.env[key];
        else process.env[key] = value;
    }));
    Object.assign(process.env, config);

    const forwarded = [];
    t.mock.method(globalThis, 'fetch', async (url, options) => {
        if (String(url) === issuer + '/protocol/openid-connect/certs') return Response.json({ keys: [jwk] });
        forwarded.push({ url, method: options.method, etag: options.headers['X-MDC-If-Match'] });
        return Response.json({ contract_version: '1.0' });
    });
    const signed = async (role) => 'Bearer ' + await fixture({
        resource_access: { myClient: { roles: [role] } }
    });
    const providerPath = ['providers', providerId];
    const offeringPath = ['offerings', offeringId];
    const tag = '"current-revision"';
    const remove = (path, authorization) => invoke({
        method: 'DELETE', path, authorization, extraHeaders: { 'if-match': tag, 'x-mdc-role': 'admin' }
    });
    const provider = await signed('mdc_provider');
    const consumer = await signed('mdc_consumer');
    const admin = await signed('mdc_admin');
    for (const [path, authorization] of [[providerPath, provider], [providerPath, consumer], [offeringPath, consumer]]) {
        const reply = await remove(path, authorization);
        assert.equal(reply.statusCode, 403);
        assert.equal(reply.data.error.code, 'mdc_role_forbidden');
    }
    for (const path of [['providers', 'tasowheel'], ['providers', 'precipart'], ['offerings', 'tasowheel_precision_gears']]) {
        const reply = await remove(path, admin);
        assert.equal(reply.statusCode, 403);
        assert.equal(reply.data.error.code, 'disposable_identity_required');
    }
    assert.equal(forwarded.length, 0);
    assert.equal((await remove(providerPath, admin)).statusCode, 200);
    assert.equal((await remove(offeringPath, provider)).statusCode, 200);
    assert.equal((await remove(offeringPath, admin)).statusCode, 200);
    const preview = 'https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app/api/';
    assert.deepEqual(forwarded, [providerPath, offeringPath, offeringPath].map((path) => ({
        url: preview + path.join('/'), method: 'DELETE', etag: tag
    })));
});

test('offline detail reads preserve the strong Preview revision through registration handoff and offering reload', async (t) => {
    const jwk = { ...await exportJWK(publicKey), kid, alg: 'RS256' };
    const config = { MDC_KEYCLOAK_AUDIENCE: audience, MDC_KEYCLOAK_ROLE_SOURCE: 'client', MDC_VERCEL_PROTECTION_BYPASS: 'offline-fixture-only' };
    const previous = Object.keys(config).map((key) => [key, process.env[key]]);
    t.after(() => previous.forEach(([key, value]) => {
        if (value === undefined) delete process.env[key];
        else process.env[key] = value;
    }));
    Object.assign(process.env, config);

    const providerTag = '"provider-revision"';
    const offeringTag = '"offering-revision"';
    let uncompressedOfferingTag = offeringTag;
    t.mock.method(globalThis, 'fetch', async (url, options) => {
        if (String(url) === issuer + '/protocol/openid-connect/certs') return Response.json({ keys: [jwk] });
        const path = new URL(url).pathname;
        const encoding = new Headers(options.headers).get('accept-encoding');
        assert.equal(options.method, 'GET');
        if (path === '/api/providers/' + providerId) {
            return Response.json({ contract_version: '1.0', ...provider }, { headers: { ETag: providerTag } });
        }
        if (path === '/api/providers/' + providerId + '/offerings') {
            assert.equal(encoding, null);
            return Response.json({ contract_version: '1.0', provider_id: providerId, offerings: [offering] });
        }
        assert.equal(path, '/api/offerings/' + offeringId);
        // The Preview returns a weak ETag when it compresses the offering detail.
        const etag = encoding === 'identity' ? uncompressedOfferingTag : 'W/' + offeringTag;
        return Response.json({ contract_version: '1.0', ...offering }, { headers: etag ? { ETag: etag } : {} });
    });

    const authorization = 'Bearer ' + await fixture();
    const getDetail = async (...path) => {
        const { data, statusCode, headers } = await invoke({ method: 'GET', path, authorization });
        assert.equal(statusCode, 200);
        return { data, status: statusCode, etag: headers.ETag ?? null };
    };
    const services = {
        getProvider: (id) => getDetail('providers', id),
        listProviderOfferings: async (id) => (await getDetail('providers', id, 'offerings')).data,
        getOffering: (id) => getDetail('offerings', id)
    };
    const readBack = await readBackRegistration({ providerId, offeringId }, services);
    assert.equal(readBack.kind, 'matching');
    const reloaded = await loadManagementSnapshot(providerId, offeringId, services);
    for (const snapshot of [readBack.snapshot, reloaded]) {
        assert.equal(snapshot.provider.etag, providerTag);
        assert.equal(snapshot.offering.etag, offeringTag);
        assert.equal(snapshot.offering.data.offering_id, offeringId);
    }
    assert.equal((await exactOffering(providerId, offeringId, services)).etag, offeringTag);

    for (const etag of ['W/' + offeringTag, null]) {
        uncompressedOfferingTag = etag;
        const resource = await exactOffering(providerId, offeringId, services);
        assert.equal(resource.etag, etag);
        assert.equal(strongEtag(resource.etag), false);
    }
});

test('offline default relay verifies session before forwarding and fails closed on issuer errors', async (t) => {
    const jwk = { ...await exportJWK(publicKey), kid, alg: 'RS256' };
    const keys = ['MDC_KEYCLOAK_AUDIENCE', 'MDC_KEYCLOAK_ROLE_SOURCE', 'MDC_VERCEL_PROTECTION_BYPASS'];
    const previous = keys.map((name) => process.env[name]);
    t.after(() => keys.forEach((name, i) => {
        if (previous[i] === undefined) delete process.env[name];
        else process.env[name] = previous[i];
    }));
    delete process.env.MDC_KEYCLOAK_AUDIENCE;
    delete process.env.MDC_KEYCLOAK_ROLE_SOURCE;
    process.env.MDC_VERCEL_PROTECTION_BYPASS = 'offline-fixture-only';
    let userInfoStatus = 200;
    let userInfoSubject = 'offline-user';
    const forwarded = [];
    t.mock.method(globalThis, 'fetch', async (url, options) => {
        if (String(url) === issuer + '/protocol/openid-connect/certs') return Response.json({ keys: [jwk] });
        if (String(url) === issuer + '/protocol/openid-connect/userinfo') {
            return Response.json({ sub: userInfoSubject }, { status: userInfoStatus });
        }
        forwarded.push({ url, options });
        return Response.json({ contract_version: '1.0', status: 'ok' });
    });
    const provider = 'Bearer ' + await fixture({}, { audience: null });
    const health = { method: 'GET', path: ['health'], authorization: provider, extraHeaders: { 'x-mdc-actor-id': 'offline-actor' } };
    assert.equal((await invoke(health)).statusCode, 200);
    assert.equal(forwarded.length, 1);
    assert.equal(forwarded[0].url, 'https://maasai-mdc-v1-y1vib2sq7-mdc19.vercel.app/api/health');
    assert.equal(forwarded[0].options.headers.Authorization, undefined);
    assert.equal(forwarded[0].options.headers['x-mdc-actor-id'], undefined);

    const consumer = 'Bearer ' + await fixture({
        realm_access: { roles: ['consumer'] },
        resource_access: { unrelated: { roles: ['admin'] } }
    }, { audience: null });
    const denial = await invoke({
        method: 'POST', path: ['provider-publication'], authorization: consumer, body: {},
        extraHeaders: { 'x-mdc-role': 'admin' }
    });
    assert.equal(denial.statusCode, 403);
    assert.equal(denial.data.error.code, 'mdc_role_forbidden');
    assert.equal(forwarded.length, 1);

    userInfoSubject = 'different-user';
    assert.equal((await invoke(health)).statusCode, 401);
    userInfoStatus = 401;
    assert.equal((await invoke(health)).statusCode, 401);
    userInfoStatus = 503;
    assert.equal((await invoke(health)).statusCode, 503);
    assert.equal(forwarded.length, 1);
});
