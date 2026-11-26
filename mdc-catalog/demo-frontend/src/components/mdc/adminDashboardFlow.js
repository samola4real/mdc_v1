import { isDisposableMdcId } from '../../services/mdc/stage1bScope.js';
import { exactProvider, strongEtag } from './providerManagementFlow.js';

export async function readAdminAvailability({ getBackendHealth, getCatalogFilters, normalizeCatalogFilters }) {
    const [health, catalogue] = await Promise.allSettled([
        Promise.resolve().then(getBackendHealth),
        Promise.resolve().then(getCatalogFilters).then(normalizeCatalogFilters)
    ]);
    const filters = catalogue.status === 'fulfilled' ? catalogue.value : null;
    return {
        apiStatus: health.status === 'rejected' ? 'error' : (health.value?.status === 'ok' ? 'available' : 'unavailable'),
        catalogueStatus: filters ? 'available' : 'error',
        counts: filters && {
            'Part families': filters.partFamilies.length,
            Materials: filters.materials.length,
            Processes: filters.processes.length,
            Certifications: filters.certifications.length
        }
    };
}

export function createAdminProviderLookup(services) {
    let current = null;
    return {
        invalidate() { current = null; },
        isPending() { return current !== null; },
        async load(id, apply) {
            const attempt = { id };
            current = attempt;
            let result;
            try {
                result = { provider: await exactProvider(id, services) };
            } catch (error) {
                result = { error };
            }
            if (current !== attempt) return;
            current = null;
            apply(result);
        }
    };
}

export const canDeleteAdminProvider = (provider, id) => (
    isDisposableMdcId(id) && provider?.data?.provider_id === id && strongEtag(provider.etag)
);
