import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { deleteProvider, getProvider } from '@/services/mdc/provider.service';
import { isDisposableMdcId } from '@/services/mdc/stage1bScope';
import ProviderActionResult, { DeletionReview, ProviderActionToast, useProviderActionToast } from './ProviderActionResult';
import { managementFeedback } from './providerActionFeedback';
import {
    canResumeDeletion, confirmDeletionText, deletionRequest, exactProvider, executeManagementWrite,
    observeManagementTarget, observedWrite, strongEtag, writeRecovery
} from './providerManagementFlow';
import { createRegistrationRequestGuard, safeText } from './providerRegistrationFlow';

const services = { deleteProvider, getProvider };
const emptyLookup = { provider: null, recovery: null, result: null };

export default function AdminProviderDeletion() {
    const [lookupId, setLookupId] = useState('');
    const [state, setState] = useState(emptyLookup);
    const [busy, setBusy] = useState('');
    const [runOnce] = useState(createRegistrationRequestGuard);
    const { toast, notify } = useProviderActionToast();
    const { provider, recovery, result } = state;
    const id = lookupId.trim();
    const record = provider?.data;
    const disposable = isDisposableMdcId(record?.provider_id);
    const canDelete = disposable && record.provider_id === id && strongEtag(provider.etag) && !recovery;

    const run = (label, providerId, operation) => runOnce(async () => {
        setBusy(label);
        try {
            await operation();
        } catch (error) {
            const message = error?.status === 404 ? 'The requested provider could not be found.' : safeText(error?.message);
            const failure = { kind: 'readError', message, target: { providerId } };
            setState((current) => ({ ...current, result: failure }));
            notify(managementFeedback(failure));
        } finally {
            setBusy('');
        }
    });

    const lookup = (event) => {
        event.preventDefault();
        if (busy || !id) return;
        if (recovery && !window.confirm('Leave the current provider deletion review and load this provider?')) return;
        return run('Loading provider', id, async () => {
            setState(emptyLookup);
            const resource = await exactProvider(id, services);
            setState({ ...emptyLookup, provider: resource });
        });
    };

    const applyDeletion = (outcome) => {
        const removed = observedWrite(outcome.request, outcome.observed);
        setState((current) => ({
            provider: removed ? null : current.provider,
            recovery: removed ? null : writeRecovery(outcome),
            result: outcome
        }));
        notify(managementFeedback(outcome));
    };

    const remove = () => {
        if (busy || !canDelete) return;
        const request = deletionRequest('provider', provider);
        return run('Deleting provider', request.providerId, async () => {
            if (!window.confirm(confirmDeletionText(request, record))) return;
            applyDeletion(await executeManagementWrite(request, services));
        });
    };

    const check = () => {
        if (busy || !recovery) return;
        return run('Checking current provider', recovery.request.providerId, async () => {
            const observed = await observeManagementTarget(recovery.request, services);
            const checked = { ...recovery, observed, checked: true };
            if (observedWrite(recovery.request, observed)) applyDeletion(checked);
            else setState((current) => ({ ...current, recovery: checked }));
        });
    };

    const resume = () => {
        if (busy || !canResumeDeletion(recovery)) return;
        setState((current) => ({ ...current, provider: recovery.observed.resource, recovery: null }));
    };

    return (
        <Panel header="Provider deletion">
            <ProviderActionToast toast={toast} />
            <form className="flex flex-wrap align-items-end gap-2 mb-3" onSubmit={lookup}>
                <div className="flex flex-column gap-2">
                    <label htmlFor="adminProviderLookup" className="font-medium">Provider ID to look up</label>
                    <InputText id="adminProviderLookup" value={lookupId} disabled={Boolean(busy)}
                        onChange={(event) => setLookupId(event.target.value)} />
                </div>
                <Button type="submit" label="Load provider" icon="pi pi-search" outlined disabled={Boolean(busy) || !id} />
            </form>
            {busy && <p role="status">{busy}…</p>}
            {record && <p><strong>Loaded provider</strong> {record.provider_name} ({record.provider_id})</p>}
            {record && !disposable && <Message severity="info" text="This provider is read-only in the Stage 1B demo." />}
            {disposable && !strongEtag(provider.etag) && <Message severity="warn" text="Load a current provider revision to delete this provider." />}
            {canDelete && <Button type="button" label="Delete provider" icon="pi pi-trash" severity="danger" outlined
                disabled={Boolean(busy)} onClick={remove} />}
            <ProviderActionResult result={result} />
            <DeletionReview recovery={recovery} busy={Boolean(busy)} onCheck={check} onResume={resume} />
        </Panel>
    );
}
