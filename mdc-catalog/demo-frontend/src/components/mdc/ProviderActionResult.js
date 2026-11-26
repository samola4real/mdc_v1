import React, { useRef } from 'react';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import { actionToastMessage, managementFeedback } from './providerActionFeedback';
import { readableCode } from './providerManagementDraft';
import { canResumeDeletion, strongEtag } from './providerManagementFlow';

export function useProviderActionToast() {
    const toast = useRef(null);
    const notify = (feedback) => {
        if (!feedback) return;
        toast.current?.clear();
        toast.current?.show(actionToastMessage(feedback));
    };
    return { toast, notify };
}

export function ProviderActionToast({ toast }) {
    return <Toast ref={toast} position="top-right" />;
}

export default function ProviderActionResult({ result, feedback = managementFeedback(result), label = 'Latest action' }) {
    if (!feedback) return null;
    const { receipt, messages } = result;
    const { providerId, offeringId } = result.request || result.identity || result.target || {};
    return (
        <div role="group" aria-label={label} className="my-2 text-sm line-height-3" style={{ overflowWrap: 'anywhere' }}>
            <p className="m-0">
                <strong>{feedback.summary}.</strong>{feedback.detail && ' ' + feedback.detail}
            </p>
            {(providerId || offeringId) && (
                <p className="m-0">{[providerId && 'Provider ID ' + providerId, offeringId && 'Offering ID ' + offeringId]
                    .filter(Boolean).join(' · ')}</p>
            )}
            {receipt?.publicationId && <p className="m-0">Publication receipt {receipt.publicationId}</p>}
            {(receipt?.publicationStatus || receipt?.syncStatus) && (
                <p className="m-0">{[receipt.publicationStatus && 'Publication ' + readableCode(receipt.publicationStatus),
                    receipt.syncStatus && 'Synchronization ' + readableCode(receipt.syncStatus)].filter(Boolean).join(' · ')}</p>
            )}
            {messages?.map((message) => <p className="m-0" key={message}>{message}</p>)}
        </div>
    );
}

export function DeletionReview({ recovery, busy, onCheck, onResume }) {
    if (!recovery) return null;
    const { request, observed, checked } = recovery;
    const { entity } = request;
    const id = request.offeringId || request.providerId;
    const latest = observed?.resource;
    const name = latest?.data[entity + '_name'];
    const guidance = recovery.kind === 'conflict' ? 'The revision changed. Review the current record before trying again.'
        : 'Check the current record to verify the deletion outcome.';
    return (
        <div role="group" aria-label={'Review ' + entity + ' deletion for ' + id} className="my-2 text-sm line-height-3">
            <p className="m-0"><strong>Review deletion of {id}.</strong> {guidance}</p>
            {checked && (
                <p className="my-1" role="status">{latest
                    ? 'Current ' + entity + ' ' + name + ' (' + id + ').'
                        + (strongEtag(latest.etag) ? '' : ' A current strong revision is required.')
                    : 'The current record could not be verified.'}</p>
            )}
            <div className="flex flex-wrap gap-2">
                <Button type="button" label={'Check current ' + entity} size="small" outlined disabled={busy} onClick={onCheck} />
                {canResumeDeletion(recovery) && (
                    <Button type="button" label={'Resume ' + entity + ' actions'} size="small" outlined disabled={busy} onClick={onResume} />
                )}
            </div>
        </div>
    );
}
