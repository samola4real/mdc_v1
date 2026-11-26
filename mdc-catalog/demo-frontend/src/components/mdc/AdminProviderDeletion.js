import React, { useEffect, useState } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { deleteProvider, getProvider } from '@/services/mdc/provider.service';
import { isDisposableMdcId } from '@/services/mdc/stage1bScope';
import ProviderActionResult, { DeletionReview, ProviderActionToast, useProviderActionToast } from './ProviderActionResult';
import { canDeleteAdminProvider, createAdminProviderLookup } from './adminDashboardFlow';
import { managementFeedback } from './providerActionFeedback';
import {
    canResumeDeletion, confirmDeletionText, deletionRequest, executeManagementWrite,
    observeManagementTarget, observedWrite, strongEtag, writeRecovery
} from './providerManagementFlow';
import { createRegistrationRequestGuard, safeText } from './providerRegistrationFlow';

const services = { deleteProvider, getProvider };
const emptyLookup = { provider: null, recovery: null, result: null, loading: false };

export default function AdminProviderDeletion() {
    const [lookupId, setLookupId] = useState('');
    const [state, setState] = useState(emptyLookup);
    const [busy, setBusy] = useState('');
    const [providerLookup] = useState(() => createAdminProviderLookup(services));
    const [runOnce] = useState(createRegistrationRequestGuard);
    const { toast, notify } = useProviderActionToast();
    const { provider, recovery, result, loading } = state;
    const id = lookupId.trim();
    const record = provider?.data.provider_id === id ? provider.data : null;
    const disposable = isDisposableMdcId(record?.provider_id);
    const canDelete = !loading && !recovery && canDeleteAdminProvider(provider, id);

    useEffect(() => providerLookup.invalidate, [providerLookup]);

    const reportReadError = (providerId, error) => {
        const message = error?.status === 404 ? 'The requested provider could not be found.' : safeText(error?.message);
        const failure = { kind: 'readError', message, target: { providerId } };
        setState((current) => ({ ...current, loading: false, result: failure }));
        notify(managementFeedback(failure));
    };

    const run = (label, providerId, operation) => runOnce(async () => {
        setBusy(label);
        try {
            await operation();
        } catch (error) {
            reportReadError(providerId, error);
        } finally {
            setBusy('');
        }
    });

    const changeLookupId = (event) => {
        if (busy) return;
        const value = event.target.value;
        if (value.trim() !== id) {
            providerLookup.invalidate();
            toast.current?.clear();
            setState((current) => ({
                ...emptyLookup,
                recovery: current.recovery && { ...current.recovery, checked: false }
            }));
        }
        setLookupId(value);
    };

    const lookup = (event) => {
        event.preventDefault();
        if (busy || !id || providerLookup.isPending()) return;
        if (recovery && !window.confirm('Leave the current provider deletion review and load this provider?')) return;
        toast.current?.clear();
        setState({ ...emptyLookup, loading: true });
        return providerLookup.load(id, ({ provider: resource, error }) => {
            if (resource) setState({ ...emptyLookup, provider: resource });
            else reportReadError(id, error);
        });
    };

    const applyDeletion = (outcome) => {
        const removed = observedWrite(outcome.request, outcome.observed);
        setState((current) => ({
            ...emptyLookup,
            provider: removed ? null : current.provider,
            recovery: removed ? null : writeRecovery(outcome),
            result: outcome
        }));
        notify(managementFeedback(outcome));
    };

    const remove = () => {
        if (busy || !canDelete || providerLookup.isPending()) return;
        const request = deletionRequest('provider', provider);
        return run('Deleting provider', request.providerId, async () => {
            if (!window.confirm(confirmDeletionText(request, record))) return;
            applyDeletion(await executeManagementWrite(request, services));
        });
    };

    const check = () => {
        if (busy || !recovery || providerLookup.isPending()) return;
        return run('Checking current provider', recovery.request.providerId, async () => {
            const observed = await observeManagementTarget(recovery.request, services);
            const checked = { ...recovery, observed, checked: true };
            if (observedWrite(recovery.request, observed)) applyDeletion(checked);
            else setState((current) => ({ ...current, recovery: checked }));
        });
    };

    const resume = () => {
        if (busy || !canResumeDeletion(recovery)) return;
        setState((current) => ({
            ...current, provider: recovery.request.providerId === id ? recovery.observed.resource : null, recovery: null
        }));
    };

    return (
        <Panel header="Provider management">
            <ProviderActionToast toast={toast} />
            <form className="flex flex-wrap align-items-end gap-2 mb-3" onSubmit={lookup}>
                <div className="flex flex-column gap-2">
                    <label htmlFor="adminProviderLookup" className="font-medium">Provider ID to look up</label>
                    <InputText id="adminProviderLookup" value={lookupId} disabled={Boolean(busy)} onChange={changeLookupId} />
                </div>
                <Button type="submit" label="Load provider" icon="pi pi-search" outlined disabled={Boolean(busy) || loading || !id} />
            </form>
            {(busy || loading) && <p role="status">{busy || 'Loading provider'}…</p>}
            {record && (
                <div role="group" aria-label="Loaded provider" className="surface-card border-1 surface-border border-round p-3 mb-3">
                    <h2 className="m-0 text-xl" style={{ overflowWrap: 'anywhere' }}>{record.provider_name}</h2>
                    <dl className="flex flex-wrap gap-3 mt-2 mb-0 text-sm">
                        <div><dt className="font-medium">Country</dt><dd className="m-0">{record.country || 'Unavailable'}</dd></div>
                        <div style={{ overflowWrap: 'anywhere', minWidth: 0 }}>
                            <dt className="font-medium">Provider ID</dt><dd className="m-0">{record.provider_id}</dd>
                        </div>
                    </dl>
                </div>
            )}
            {record && !disposable && <Message severity="info" text="This provider is read-only in the Stage 1B demo." />}
            {disposable && !strongEtag(provider.etag) && <Message severity="warn" text="Load a current provider revision to delete this provider." />}
            {canDelete && <Button type="button" label="Delete provider" icon="pi pi-trash" severity="danger" outlined
                disabled={Boolean(busy)} onClick={remove} />}
            <ProviderActionResult result={result} />
            <DeletionReview recovery={recovery} busy={Boolean(busy)} onCheck={check} onResume={resume} />
        </Panel>
    );
}
