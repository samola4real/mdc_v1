import { isDisposableMdcId, isDisposableOfferingId } from '../../services/mdc/stage1bScope.js';
import { sameValue } from './providerManagementDraft.js';
import { registrationValidationFeedback, safeText } from './providerRegistrationFlow.js';

export const strongEtag = (value) => typeof value === 'string' && /^"[\x21\x23-\x7e\x80-\xff]+"$/.test(value);

export const isDisposableOfferingRow = (providerId, row) => (
    isDisposableMdcId(providerId) && isDisposableOfferingId(row?.offering_id, providerId)
    && (!row.provider_id || row.provider_id === providerId)
);

export async function exactProvider(id, services) {
    const result = await services.getProvider(id);
    if (result?.data?.provider_id !== id) throw new Error('The provider response did not match the requested ID.');
    return result;
}

export async function exactOffering(providerId, id, services) {
    const result = await services.getOffering(id);
    if (result?.data?.offering_id !== id || result.data.provider_id !== providerId) {
        throw new Error('The offering response did not match the requested provider and offering.');
    }
    return result;
}

export async function exactList(id, services) {
    const result = await services.listProviderOfferings(id);
    if (result?.provider_id !== id || !Array.isArray(result.offerings)
        || !result.offerings.every((row) => row.offering_id && (!row.provider_id || row.provider_id === id))) {
        throw new Error('The offering list did not match the requested provider.');
    }
    return result;
}

export async function loadManagementSnapshot(providerId, preferredId, services) {
    const provider = await exactProvider(providerId, services);
    const list = await exactList(providerId, services);
    const id = preferredId === undefined ? list.offerings[0]?.offering_id : preferredId;
    const offering = list.offerings.some((row) => row.offering_id === id) ? await exactOffering(providerId, id, services) : null;
    return { provider, list, offering };
}

const targetId = (request) => request.entity === 'provider' ? request.providerId : request.offeringId;
const isProvider = (request) => request.entity === 'provider';

function matchingResource(resource, request) {
    return Object.entries(request.payload).every(([key, value]) => sameValue(resource.data[key], value));
}

export async function observeManagementTarget(request, services) {
    try {
        const resource = await (isProvider(request) ? exactProvider(request.providerId, services)
            : exactOffering(request.providerId, request.offeringId, services));
        const matches = request.operation !== 'delete' && matchingResource(resource, request);
        return { kind: 'present', resource, matches };
    } catch (error) {
        const absence = error?.status === 404 && ['not_found', request.entity + '_not_found'].includes(error.code);
        return { kind: absence ? 'absent' : 'unknown' };
    }
}

export const observedWrite = (request, observed) => (
    request.operation === 'delete' ? observed?.kind === 'absent' : observed?.kind === 'present' && observed.matches
);

export function deletionRequest(entity, resource) {
    const { provider_id: providerId, offering_id: offeringId } = resource.data;
    return { entity, operation: 'delete', providerId, offeringId: entity === 'offering' ? offeringId : undefined, etag: resource.etag };
}

export function confirmDeletionText(request, record) {
    if (request.entity === 'provider') {
        return 'Permanently delete provider ' + record.provider_name + ' (' + request.providerId
            + ') and all of its offerings?';
    }
    return 'Permanently delete offering ' + record.offering_name + ' (' + request.offeringId
        + ') from provider ' + request.providerId + '?';
}

export const canResumeDeletion = (recovery) => Boolean(
    recovery?.checked && recovery.observed?.kind === 'present' && strongEtag(recovery.observed.resource.etag)
);

export function clearOfferingDeletion(deletions, id) {
    const next = { ...deletions };
    delete next[id];
    return next;
}

export function afterVerifiedOfferingDeletion(workspace, outcome) {
    if (!observedWrite(outcome.request, outcome.observed)) return workspace;
    const { offeringId } = outcome.request;
    return {
        ...workspace,
        ...(workspace.selection === offeringId && { selection: null, offering: null }),
        offerings: workspace.offerings.filter((row) => row.offering_id !== offeringId),
        offeringDeletions: clearOfferingDeletion(workspace.offeringDeletions, offeringId),
        result: outcome
    };
}

const receiptDetails = (data, error) => ({
    publicationId: safeText(data?.publication_id ?? error?.publicationId),
    publicationStatus: safeText(data?.publication_status ?? error?.publicationStatus),
    syncStatus: safeText(data?.sync_status ?? error?.syncStatus)
});

function receiptMatches(response, request) {
    const data = response?.data;
    const creation = request.operation === 'create';
    if (response?.status !== (creation ? 201 : 200) || data?.contract_version !== '1.0'
        || data.provider_id !== request.providerId || !receiptDetails(data).publicationId) return false;
    const statusMatches = (data.status === 'accepted' && data.publication_status === 'sync_pending' && data.sync_status === 'pending')
        || (data.status === 'completed' && data.publication_status === 'synced' && data.sync_status === 'succeeded');
    if (!statusMatches) return false;
    if (request.operation === 'delete') {
        return data.operation === 'delete' && data.target?.entity_type === request.entity && data.target.entity_id === targetId(request);
    }
    if (data.operation !== 'update') return false;
    return isProvider(request) || (data.offering_id === request.offeringId && data.offering_ids?.length === 1
        && data.offering_ids[0] === request.offeringId);
}

const validationFeedback = (error, request) => registrationValidationFeedback(
    error?.details, { offerings: [request.offering || {}] }, request.operation === 'save' && !isProvider(request)
);

export async function executeManagementWrite(request, services) {
    const { operation, providerId, offeringId, payload, etag } = request;
    if (!isDisposableMdcId(providerId) || (!isProvider(request) && !isDisposableOfferingId(offeringId, providerId))
        || (operation !== 'create' && !strongEtag(etag))) return { kind: 'blocked', request };

    let response;
    try {
        if (operation === 'create') response = await services.createOffering(providerId, payload);
        else if (operation === 'delete') {
            response = await (isProvider(request) ? services.deleteProvider(providerId, etag) : services.deleteOffering(offeringId, etag));
        } else {
            response = await (isProvider(request) ? services.updateProvider(providerId, payload, etag)
                : services.updateOffering(offeringId, payload, etag));
        }
    } catch (error) {
        const receipt = receiptDetails(null, error);
        if (error?.status === 412 || error?.status === 428) return { kind: 'conflict', request, receipt };
        if (error?.status >= 400 && error?.status < 500 && error?.status !== 408) {
            return { kind: 'rejected', request, receipt, status: error.status, code: safeText(error.code),
                message: safeText(error.message), ...validationFeedback(error, request) };
        }
        return { kind: 'uncertain', request, receipt, observed: await observeManagementTarget(request, services) };
    }
    const accepted = receiptMatches(response, request);
    return {
        kind: accepted ? 'accepted' : 'uncertain', request, receipt: accepted ? receiptDetails(response.data) : undefined,
        observed: await observeManagementTarget(request, services)
    };
}

export function acceptParentRevision(editor, latest) {
    if (editor.resource.data.provider_id !== latest?.data?.provider_id || !strongEtag(latest.etag) || editor.recovery) return editor;
    const providerFields = (data) => Object.fromEntries(Object.entries(data).filter(([key]) => key !== 'offerings'));
    if (!sameValue(providerFields(editor.resource.data), providerFields(latest.data))) return editor;
    return { ...editor, resource: latest };
}

export function writeRecovery(outcome) {
    if (outcome.kind === 'conflict') return outcome;
    if (!['accepted', 'uncertain'].includes(outcome.kind)) return null;
    return observedWrite(outcome.request, outcome.observed) ? null : outcome;
}
