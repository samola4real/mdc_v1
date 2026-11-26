import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
    canDeleteAdminProvider, createAdminProviderLookup, readAdminAvailability
} from '../src/components/mdc/adminDashboardFlow.js';
import {
    canResumeDeletion, confirmDeletionText, deletionRequest, executeManagementWrite, observeManagementTarget,
    observedWrite, writeRecovery
} from '../src/components/mdc/providerManagementFlow.js';

const firstId = 'mdc_stage1b_admin_lookup_a';
const secondId = 'mdc_stage1b_admin_lookup_b';
const resource = (id, etag = '"loaded-revision"') => ({
    data: { provider_id: id, provider_name: 'Fixture ' + id, country: 'Finland' }, etag
});
const unknownProvider = () => { throw { status: 404, code: 'provider_not_found' }; };

test('Admin lookup returns the exact record and reports failed or mismatched reads', async () => {
    const loaded = resource(firstId);
    const lookup = createAdminProviderLookup({
        getProvider: async (id) => id === secondId ? unknownProvider() : loaded
    });
    const outcomes = [];
    const apply = (result) => outcomes.push(result);
    await lookup.load(firstId, apply);
    await lookup.load(secondId, apply);
    await lookup.load('different', apply);
    assert.strictEqual(outcomes[0].provider, loaded);
    assert.equal(outcomes[1].error.status, 404);
    assert.match(outcomes[2].error.message, /did not match the requested ID/);
    assert.equal(lookup.isPending(), false);
});

test('editing away from a lookup suppresses its late success or error even before another lookup', async () => {
    for (const end of ['resolve', 'reject']) {
        const deferred = Promise.withResolvers();
        const lookup = createAdminProviderLookup({ getProvider: () => deferred.promise });
        const pending = lookup.load(firstId, () => assert.fail('An invalidated lookup updated the dashboard'));
        assert.equal(lookup.isPending(), true);
        lookup.invalidate();
        deferred[end](end === 'resolve' ? resource(firstId) : new Error('stale failure'));
        await pending;
        assert.equal(lookup.isPending(), false);
    }
});

test('only the latest exact Admin lookup can populate the summary when reads resolve out of order', async () => {
    const first = Promise.withResolvers();
    const second = Promise.withResolvers();
    const lookup = createAdminProviderLookup({ getProvider: (id) => id === firstId ? first.promise : second.promise });
    const outcomes = [];
    const pendingFirst = lookup.load(firstId, (result) => outcomes.push(result));
    const pendingSecond = lookup.load(secondId, (result) => outcomes.push(result));
    const latest = resource(secondId, '"latest-revision"');
    second.resolve(latest);
    await pendingSecond;
    first.resolve(resource(firstId));
    await pendingFirst;
    assert.deepEqual(outcomes, [{ provider: latest }]);
    assert.equal(lookup.isPending(), false);
});

test('Admin delete eligibility requires the loaded ID, disposable scope and its strong revision', () => {
    assert.equal(canDeleteAdminProvider(resource(firstId), firstId), true);
    assert.equal(canDeleteAdminProvider(resource(firstId), secondId), false);
    assert.equal(canDeleteAdminProvider(null, firstId), false);
    for (const tag of [null, 'W/"weak"', 'unquoted']) {
        assert.equal(canDeleteAdminProvider(resource(firstId, tag), firstId), false);
    }
    for (const baseline of ['tasowheel', 'precipart']) {
        assert.equal(canDeleteAdminProvider(resource(baseline), baseline), false);
    }
});

test('Admin provider deletion uses its exact loaded revision and requires read-back absence', async () => {
    const loaded = resource(firstId);
    const request = deletionRequest('provider', loaded);
    assert.match(confirmDeletionText(request, loaded.data), new RegExp(firstId + '.*and all of its offerings'));
    const outcome = await executeManagementWrite(request, {
        deleteProvider: (id, etag) => {
            assert.deepEqual([id, etag], [firstId, loaded.etag]);
            return { status: 200, data: {
                contract_version: '1.0', operation: 'delete', provider_id: firstId, publication_id: 'admin-delete',
                status: 'accepted', publication_status: 'sync_pending', sync_status: 'pending',
                target: { entity_type: 'provider', entity_id: firstId }
            } };
        },
        getProvider: (id) => {
            assert.equal(id, firstId);
            return unknownProvider();
        }
    });
    assert.equal(outcome.kind, 'accepted');
    assert.equal(observedWrite(request, outcome.observed), true);
    assert.equal(writeRecovery(outcome), null);
});

test('Admin provider delete conflicts require review and ambiguous reads cannot trigger a retry', async () => {
    const request = deletionRequest('provider', resource(firstId));
    let writes = 0;
    const conflict = await executeManagementWrite(request, {
        deleteProvider: () => { writes++; throw { status: 412 }; },
        getProvider: () => assert.fail('A stale deletion must wait for explicit review')
    });
    assert.equal(writeRecovery(conflict), conflict);
    const updated = await observeManagementTarget(request, { getProvider: async () => resource(firstId, '"current-revision"') });
    assert.equal(canResumeDeletion({ ...conflict, observed: updated }), false);
    assert.equal(canResumeDeletion({ ...conflict, observed: updated, checked: true }), true);

    const ambiguous = await executeManagementWrite(request, {
        deleteProvider: () => { writes++; throw { status: 503 }; },
        getProvider: () => { throw { status: 404, code: 'mdc_route_not_found' }; }
    });
    assert.equal(writeRecovery(ambiguous), ambiguous);
    assert.equal(ambiguous.observed.kind, 'unknown');
    const checked = await observeManagementTarget(request, { getProvider: unknownProvider });
    assert.equal(observedWrite(request, checked), true);
    assert.equal(writes, 2);
});

const availability = (health, filters) => readAdminAvailability({
    getBackendHealth: health,
    getCatalogFilters: filters,
    normalizeCatalogFilters: (data) => {
        if (!data) throw new Error('Invalid catalogue response');
        return data.options;
    }
});
const filterResponse = { options: { partFamilies: ['gear', 'shaft'], materials: ['steel'], processes: [], certifications: ['ISO', 'sample'] } };

test('dashboard availability and counts come from the current API and normalized catalogue responses', async () => {
    const actual = await availability(async () => ({ status: 'ok' }), async () => filterResponse);
    assert.deepEqual(actual, {
        apiStatus: 'available', catalogueStatus: 'available',
        counts: { 'Part families': 2, Materials: 1, Processes: 0, Certifications: 2 }
    });
});

test('dashboard failures stay independent and an unavailable catalogue has no counts', async () => {
    const unavailable = await availability(async () => ({ status: 'unavailable' }), async () => null);
    assert.deepEqual(unavailable, { apiStatus: 'unavailable', catalogueStatus: 'error', counts: null });
    const failed = await availability(() => { throw new Error('API check failed'); }, async () => filterResponse);
    assert.equal(failed.apiStatus, 'error');
    assert.equal(failed.catalogueStatus, 'available');
    assert.equal(failed.counts.Materials, 1);
});

test('the Admin view keeps its guard and renders the accepted dashboard blocks without raw responses', () => {
    const read = (path) => readFileSync(new URL('../src/' + path, import.meta.url), 'utf8');
    const page = read('pages/demo/admin-audit.js');
    const view = read('components/mdc/AdminAuditPanel.js');
    const provider = read('components/mdc/AdminProviderDeletion.js');
    assert.match(page, /<h1[^>]*>Admin Dashboard<\/h1>/);
    assert.match(page, /<DemoRoleGuard allowedRoles=\{\['admin'\]\}/);
    assert.match(view, /Backend API[\s\S]*<AdminProviderDeletion\s*\/>[\s\S]*Catalogue overview/);
    assert.match(provider, /header="Provider management"/);
    assert.match(provider, /window\.confirm\(confirmDeletionText\(request, record\)\)/);
    assert.doesNotMatch(view, /<pre\b|JSON\.stringify|Health response|Catalogue filter response|search readiness/);
});
