import { useEffect, useState } from 'react';
import {
    createOffering, deleteOffering, getOffering, getProvider, listProviderOfferings, updateOffering, updateProvider
} from '@/services/mdc/provider.service';
import { isDisposableMdcId, isDisposableOfferingId } from '@/services/mdc/stage1bScope';
import {
    buildAddedOffering, buildOfferingEdit, buildProviderEdit, editorDirty, offeringEditor, providerEditor
} from './providerManagementDraft';
import { emptyRegistrationForm, hasRegistrationDraft } from './providerRegistrationPayload';
import { createRegistrationRequestGuard, safeText } from './providerRegistrationFlow';
import {
    acceptParentRevision, afterVerifiedOfferingDeletion, canResumeDeletion, clearOfferingDeletion, confirmDeletionText,
    deletionRequest, exactList, exactOffering, exactProvider, executeManagementWrite, isDisposableOfferingRow,
    loadManagementSnapshot, observeManagementTarget, observedWrite, strongEtag, writeRecovery
} from './providerManagementFlow';

const services = { createOffering, deleteOffering, getOffering, getProvider, listProviderOfferings, updateOffering, updateProvider };
const emptyWorkspace = () => ({
    provider: null, offering: null, offerings: [], selection: null, add: null, result: null, offeringDeletions: {}
});
const editors = { provider: providerEditor, offering: offeringEditor };
const pendingEdits = (editor) => Boolean(editorDirty(editor) || editor?.previousDraft || editor?.recovery);

function openedWorkspace({ provider, offering, list }, selection = null) {
    return {
        ...emptyWorkspace(), provider: providerEditor(provider), offering: offering && offeringEditor(offering),
        offerings: list.offerings, selection: offering?.data.offering_id ?? selection
    };
}

function replaceOffering(rows, request, record) {
    return rows.some(({ offering_id }) => offering_id === request.offeringId)
        ? rows.map((row) => row.offering_id === request.offeringId ? record : row) : [...rows, record];
}

function refreshedOfferingRows(workspace, rows) {
    const listed = new Set(rows.map(({ offering_id }) => offering_id));
    return [...rows, ...workspace.offerings.filter(({ offering_id }) =>
        Object.hasOwn(workspace.offeringDeletions, offering_id) && !listed.has(offering_id))];
}

function updateParentEditor(current, latest) {
    if (!latest || current.recovery || !strongEtag(latest.etag)) return current;
    const refreshed = acceptParentRevision(current, latest);
    if (refreshed !== current) return refreshed;
    if (!pendingEdits(current)) return providerEditor(latest);
    return {
        ...current, recovery: {
            kind: 'conflict', observed: { kind: 'present', resource: latest },
            request: { entity: 'provider', operation: 'save', providerId: current.resource.data.provider_id, payload: {} }
        }
    };
}

export function useProviderManagement(filters, onRegistrationReadBack, onActionResult) {
    const [state, setState] = useState(emptyWorkspace);
    const [lookupId, setLookupId] = useState('');
    const [busy, setBusy] = useState(null);
    const [runOnce] = useState(createRegistrationRequestGuard);
    const { provider, offering, add, offeringDeletions } = state;
    const providerId = provider?.resource.data.provider_id;
    const offeringId = offering?.resource.data.offering_id;
    const manageable = isDisposableMdcId(providerId);
    const manageableOffering = manageable && isDisposableOfferingId(offeringId, providerId);
    const providerEditable = manageable && strongEtag(provider.resource.etag);
    const offeringEditable = manageableOffering && strongEtag(offering.resource.etag);
    const providerChanges = providerEditable ? buildProviderEdit(provider, filters) : null;
    const offeringChanges = offeringEditable ? buildOfferingEdit(offering, filters) : null;
    const newOffering = add && buildAddedOffering(add.draft, provider.resource.data, filters);
    const providerPending = pendingEdits(provider);
    const offeringPending = pendingEdits(offering);
    const addPending = add && (hasRegistrationDraft(add.draft) || add.recovery);
    const dirty = Boolean(providerPending || offeringPending || addPending || Object.keys(offeringDeletions).length);

    useEffect(() => {
        if (!dirty) return undefined;
        const warn = (event) => {
            event.preventDefault();
            event.returnValue = '';
        };
        window.addEventListener('beforeunload', warn);
        return () => window.removeEventListener('beforeunload', warn);
    }, [dirty]);

    const confirmDiscard = (hasEdits, action) => !hasEdits || window.confirm(
        'You have unsaved changes or a write awaiting review. Discard this draft and ' + action + '?'
    );
    const run = (label, operation, target) => runOnce(async () => {
        setBusy(label);
        try {
            await operation();
        } catch (error) {
            const message = error?.status === 404 ? 'The requested record could not be found.'
                : error?.status === 401 || error?.status === 403 ? 'The current session cannot access the requested record.'
                    : safeText(error?.message);
            const result = { kind: 'readError', message, target };
            setState((current) => ({ ...current, result }));
            onActionResult(result);
        } finally {
            setBusy(null);
        }
    });

    const acceptRegistration = ({ identity, readBack }) => {
        setLookupId(identity.providerId);
        setState(readBack.kind === 'matching' ? openedWorkspace(readBack.snapshot)
            : { ...emptyWorkspace(), selection: identity.offeringId, registrationTarget: identity });
    };

    const lookup = () => {
        const id = lookupId.trim();
        if (!id || busy || !confirmDiscard(dirty, 'load this provider')) return;
        return run('Loading provider', async () => {
            const registrationTarget = state.registrationTarget?.providerId === id ? state.registrationTarget : null;
            const desired = registrationTarget ? registrationTarget.offeringId : id === providerId ? state.selection : undefined;
            const snapshot = await loadManagementSnapshot(id, desired, services);
            const next = openedWorkspace(snapshot, desired);
            if (registrationTarget && snapshot.offering) onRegistrationReadBack(snapshot);
            else if (registrationTarget) next.registrationTarget = registrationTarget;
            if (desired && !snapshot.offering) {
                next.result = {
                    kind: 'notice', target: { providerId: id, offeringId: desired },
                    message: 'The selected offering could not be found for this provider. Choose a row to inspect another offering.'
                };
                onActionResult(next.result);
            }
            setLookupId(id);
            setState(next);
        }, { providerId: id });
    };

    const chooseOffering = (id) => {
        if (!id || id === offeringId || busy || !confirmDiscard(offeringPending || addPending, 'switch offerings')) return;
        return run('Loading offering', async () => {
            const result = await exactOffering(providerId, id, services);
            setState((current) => ({ ...current, offering: offeringEditor(result), selection: id, add: null, result: null }));
        }, { providerId, offeringId: id });
    };

    const startAdd = () => {
        if (!manageable || !filters || busy || add || !confirmDiscard(offeringPending, 'add an offering')) return;
        setState((current) => ({
            ...current,
            offering: offering && offeringEditor(offering.resource),
            add: { draft: emptyRegistrationForm() }, result: null
        }));
    };

    const cancelAdd = () => {
        if (busy || !confirmDiscard(addPending, 'return to the selected offering')) return;
        setState((current) => ({ ...current, add: null, result: null }));
    };

    const change = (entity, draft) => {
        setState((current) => ({
            ...current, [entity]: { ...current[entity], draft },
            result: current.result?.kind === 'rejected' && current.result.request?.operation !== 'delete'
                && current.result.request?.entity === (entity === 'add' ? 'offering' : entity)
                ? null : current.result
        }));
    };

    const applyWrite = async (outcome) => {
        const { request, observed } = outcome;
        const key = request.operation === 'create' ? 'add' : request.entity;
        const recovery = writeRecovery(outcome);
        onActionResult(outcome);
        if (recovery || !observedWrite(request, observed)) {
            setState((current) => ({
                ...current,
                [key]: { ...current[key], recovery,
                    ...(key === 'add' && outcome.code === 'offering_already_exists' && { duplicateId: request.offeringId }) },
                result: outcome
            }));
            return;
        }
        if (request.entity === 'provider') {
            setState((current) => ({ ...current, provider: providerEditor(observed.resource), result: outcome }));
            return;
        }
        const [parent, list] = await Promise.allSettled([exactProvider(request.providerId, services), exactList(request.providerId, services)]);
        setState((current) => ({
            ...current, add: null,
            provider: updateParentEditor(current.provider, parent.status === 'fulfilled' && parent.value),
            offering: offeringEditor(observed.resource),
            selection: request.offeringId,
            offerings: list.status === 'fulfilled' ? refreshedOfferingRows(current, list.value.offerings)
                : replaceOffering(current.offerings, request, observed.resource?.data),
            result: outcome
        }));
    };

    const submit = (label, request) => run(label, async () => {
        await applyWrite(await executeManagementWrite(request, services));
    });

    const canSave = (editor, changes) => !busy && changes && !editor.recovery
        && Object.keys(changes.patch).length > 0 && Object.keys(changes.errors).length === 0;
    const canSaveProvider = Boolean(canSave(provider, providerChanges));
    const canSaveOffering = !offeringDeletions[offeringId] && Boolean(canSave(offering, offeringChanges));
    const canCreate = Boolean(add && !busy && manageable && filters && !add.recovery
        && !offeringDeletions[newOffering.payload.offering_id]
        && add.duplicateId !== newOffering.payload.offering_id && Object.keys(newOffering.errors).length === 0);
    const saveRequest = (entity) => ({
        entity, operation: 'save', providerId, offeringId: entity === 'offering' ? offeringId : undefined, etag: state[entity].resource.etag
    });

    const saveProvider = () => {
        if (canSaveProvider) return submit('Saving provider', { ...saveRequest('provider'), payload: providerChanges.patch });
    };
    const saveOffering = () => {
        if (canSaveOffering) return submit('Saving offering', { ...saveRequest('offering'),
            payload: offeringChanges.patch, offering: { ...offering.resource.data, ...offeringChanges.patch } });
    };
    const addOffering = () => {
        if (canCreate) return submit('Creating offering', {
            operation: 'create', entity: 'offering', providerId, offeringId: newOffering.payload.offering_id,
            payload: newOffering.payload, offering: newOffering.payload
        });
    };

    const applyOfferingDeletion = async (outcome) => {
        const { request, observed } = outcome;
        onActionResult(outcome);
        if (!observedWrite(request, observed)) {
            const recovery = writeRecovery(outcome);
            setState((current) => ({
                ...current, result: outcome,
                ...(recovery && { offeringDeletions: { ...current.offeringDeletions, [request.offeringId]: recovery } })
            }));
            return;
        }
        const parent = await exactProvider(request.providerId, services).catch(() => null);
        setState((current) => ({
            ...afterVerifiedOfferingDeletion(current, outcome),
            provider: updateParentEditor(current.provider, parent)
        }));
    };

    const offeringDeleteDisabled = (id) => Boolean(busy || offeringDeletions[id]
        || (id === offeringId && offering?.recovery) || add?.recovery?.request.offeringId === id);
    const removeOffering = (id) => {
        const row = state.offerings.find(({ offering_id }) => offering_id === id);
        if (!isDisposableOfferingRow(providerId, row) || offeringDeleteDisabled(id)) return;
        return run('Checking offering for deletion', async () => {
            if (!confirmDiscard(id === offeringId && offeringPending, 'delete this offering')) return;
            const target = await exactOffering(providerId, id, services);
            if (!strongEtag(target.etag)) throw new Error('A current strong offering revision is required for deletion.');
            const request = deletionRequest('offering', target);
            if (!window.confirm(confirmDeletionText(request, target.data))) return;
            setBusy('Deleting offering');
            await applyOfferingDeletion(await executeManagementWrite(request, services));
        }, { providerId, offeringId: id });
    };

    const checkOfferingDeletion = (id) => {
        const recovery = offeringDeletions[id];
        if (busy || !recovery) return;
        return run('Checking current offering', async () => {
            const observed = await observeManagementTarget(recovery.request, services);
            const checked = { ...recovery, observed, checked: true };
            if (observedWrite(recovery.request, observed)) await applyOfferingDeletion(checked);
            else setState((current) => ({
                ...current, offeringDeletions: { ...current.offeringDeletions, [id]: checked }
            }));
        }, recovery.request);
    };

    const resumeOfferingActions = (id) => {
        if (busy || !canResumeDeletion(offeringDeletions[id])) return;
        setState((current) => ({ ...current, offeringDeletions: clearOfferingDeletion(current.offeringDeletions, id) }));
    };

    const checkLatest = (entity) => {
        const recovery = state[entity]?.recovery;
        if (!recovery || busy) return;
        return run('Checking current record', async () => {
            const observed = await observeManagementTarget(recovery.request, services);
            if (recovery.kind !== 'conflict' && observedWrite(recovery.request, observed)) {
                await applyWrite({ ...recovery, observed });
            } else {
                setState((current) => ({ ...current, [entity]: { ...current[entity], recovery: { ...recovery, observed } } }));
            }
        });
    };

    const useLatest = (entity) => {
        const editor = state[entity];
        const latest = editor?.recovery?.observed?.resource;
        if (busy || !latest || !strongEtag(latest.etag)) return;
        const before = editor.resource.data;
        const after = latest.data;
        if (before.provider_id !== after.provider_id || (entity === 'offering' && before.offering_id !== after.offering_id)) return;
        const previousDraft = editorDirty(editor) ? editor.draft : editor.previousDraft;
        setState((current) => ({
            ...current, result: null, [entity]: { ...editors[entity](latest), previousDraft, previousLocked: editor.locked },
            ...(entity === 'offering' && { offerings: replaceOffering(current.offerings, { offeringId, operation: 'save' }, after) })
        }));
    };

    const continueAdd = () => {
        const recovery = add?.recovery;
        if (busy || recovery?.kind !== 'uncertain' || !['absent', 'present'].includes(recovery.observed?.kind)
            || (recovery.observed.kind === 'absent' && recovery.receipt?.publicationId)) return;
        setState((current) => ({ ...current, result: null, add: {
            ...current.add, recovery: null, duplicateId: recovery.observed.kind === 'present' ? recovery.request.offeringId : undefined
        } }));
    };

    const dismissAttempt = (entity) => {
        if (!busy && window.confirm('Discard the saved copy of your attempted edits?')) {
            setState((current) => ({ ...current, [entity]: { ...current[entity], previousDraft: null, previousLocked: null } }));
        }
    };

    return {
        ...state, lookupId, setLookupId, busy, manageable, manageableOffering, providerEditable, offeringEditable,
        providerChanges, offeringChanges, newOffering, canSaveProvider, canSaveOffering, canCreate,
        acceptRegistration, lookup, chooseOffering, startAdd, cancelAdd, change, saveProvider, saveOffering, addOffering,
        removeOffering, offeringDeleteDisabled, checkOfferingDeletion, resumeOfferingActions,
        checkLatest, useLatest, continueAdd, dismissAttempt,
        canLeave: () => !busy && confirmDiscard(dirty, 'switch modes'), reset: () => setState(emptyWorkspace())
    };
}
