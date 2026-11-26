import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
    canDeleteAdminProvider, createAdminProviderLookup, readAdminAvailability
} from '../src/components/mdc/adminDashboardFlow.js';
import {
    canResumeDeletion, confirmDeletionText, deletionRequest, exactOffering, executeManagementWrite,
    loadManagementSnapshot, observeManagementTarget, observedWrite, writeRecovery
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
        apiStatus: 'available', catalogueStatus: 'available', filters: filterResponse.options,
        counts: { 'Part families': 2, Materials: 1, Processes: 0, Certifications: 2 }
    });
});

test('dashboard failures stay independent and an unavailable catalogue has no counts', async () => {
    const unavailable = await availability(async () => ({ status: 'unavailable' }), async () => null);
    assert.deepEqual(unavailable, { apiStatus: 'unavailable', catalogueStatus: 'error', filters: null, counts: null });
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
    assert.match(view, /Backend API[\s\S]*<AdminProviderDeletion filters=[\s\S]*Catalogue overview/);
    assert.match(provider, /pi-briefcase[^>]*\/>Provider management/);
    assert.match(provider, /window\.confirm\(confirmDeletionText\(request, record\)\)/);
    assert.doesNotMatch(view, /<pre\b|JSON\.stringify|Health response|Catalogue filter response|search readiness/);
});

test('View provider reads the exact protected provider and its selected offering and capabilities', async () => {
    const id = 'tasowheel';
    const first = { provider_id: id, offering_id: 'tasowheel_fixture_gear', part_family: 'gear' };
    const second = {
        provider_id: id, offering_id: 'tasowheel_fixture_shaft', part_family: 'shaft',
        family_capabilities: { length_mm: { max: 330 } }
    };
    const records = { [first.offering_id]: first, [second.offering_id]: second };
    const calls = [];
    const services = {
        getProvider: async (requested) => {
            calls.push(['provider', requested]);
            return resource(id);
        },
        listProviderOfferings: async (requested) => {
            calls.push(['list', requested]);
            return { provider_id: id, offerings: [first, second] };
        },
        getOffering: async (requested) => {
            calls.push(['offering', requested]);
            return { data: records[requested], etag: '"offering-revision"' };
        }
    };
    const snapshot = await loadManagementSnapshot(id, undefined, services);
    const selected = await exactOffering(id, second.offering_id, services);
    assert.equal(snapshot.provider.data.provider_id, id);
    assert.equal(snapshot.offering.data.offering_id, first.offering_id);
    assert.equal(selected.data.family_capabilities.length_mm.max, 330);
    assert.equal(canDeleteAdminProvider(snapshot.provider, id), false);
    assert.deepEqual(calls, [['provider', id], ['list', id], ['offering', first.offering_id], ['offering', second.offering_id]]);
});

test('View provider rejects mismatched identities before exposing details', async () => {
    const offeringId = firstId + '_metal';
    const services = {
        getProvider: async () => resource(firstId),
        listProviderOfferings: async () => ({ provider_id: firstId, offerings: [{ offering_id: offeringId }] }),
        getOffering: async () => ({ data: { provider_id: secondId, offering_id: offeringId } })
    };
    await assert.rejects(loadManagementSnapshot(firstId, undefined, services), /requested provider and offering/);
    await assert.rejects(loadManagementSnapshot(secondId, undefined, services), /provider response/);
});

test('the loaded provider card contains both actions and the dialog reuses read-only management fields', () => {
    const read = (file) => readFileSync(new URL('../src/components/mdc/' + file, import.meta.url), 'utf8');
    const card = read('AdminProviderDeletion.js');
    const view = read('AdminProviderView.js');
    assert.match(card, /\{record && \([\s\S]*aria-label="Loaded provider"[\s\S]*label="View provider"[\s\S]*\{canDelete && <Button/);
    assert.match(card, /\{record && <AdminProviderView providerId=\{record\.provider_id\}/);
    assert.match(view, /loadManagementSnapshot\(providerId, undefined, services\)/);
    assert.match(view, /exactOffering\(providerId, requestedId, services\)/);
    assert.match(view, /<ManagedFields entity="provider"[^>]+\breadOnly\b/);
    assert.match(view, /<ManagedFields key=\{offeringId\} entity="offering"[^>]+\breadOnly\b/);
    assert.doesNotMatch(view, /updateProvider|deleteProvider|updateOffering|deleteOffering|createOffering/);
});
