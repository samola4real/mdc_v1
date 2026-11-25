import React from 'react';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { readableCode } from './providerManagementDraft';
import { observedWrite } from './providerManagementFlow';

const rejectionHelp = {
    400: 'Review the highlighted information and correct the rejected fields.',
    401: 'Sign in with MaaSAI Keycloak.',
    403: 'Check your verified role and the disposable ID scope.',
    404: 'The requested record could not be found.',
    409: 'Choose a different offering ID or load the existing offering to review it.'
};

export default function ProviderActionResult({ result }) {
    if (!result) return null;
    const { request, receipt } = result;
    let severity = 'info';
    let message = result.message;
    if (request) {
        const entity = request.entity;
        if (result.kind === 'conflict') {
            severity = 'warn';
            message = 'The ' + entity + ' revision changed. Review the latest record before trying again.';
        } else if (result.kind === 'accepted') {
            severity = observedWrite(request, result.observed) ? 'success' : 'warn';
            const action = { save: 'saved', create: 'created', delete: 'deleted' }[request.operation];
            message = severity === 'success' ? readableCode(entity) + ' ' + action + '.'
                : 'The write was accepted. Check the current ' + entity + ' before making another change.';
        } else if (result.kind === 'uncertain') {
            severity = 'warn';
            message = observedWrite(request, result.observed)
                ? request.operation === 'delete' ? 'The record is absent on read-back. A write receipt could not be verified.'
                    : 'The submitted values are present on read-back. A write receipt could not be verified.'
                : 'The write outcome could not be confirmed. Check the current record before retrying.';
        } else {
            severity = 'error';
            message = [result.message || 'The request was rejected.', rejectionHelp[result.status]].filter(Boolean).join(' ');
        }
    } else if (result.kind === 'readError') {
        severity = 'error';
        message = 'The record could not be loaded.' + (message ? ' ' + message : '');
    }
    return (
        <Card className="mdc-provider-feedback">
            <div className="flex flex-column gap-2" aria-live="polite">
                <Message severity={severity} text={message} className="w-full justify-content-start" />
                {result.messages?.map((value) => <div key={value}>{value}</div>)}
                {receipt?.publicationId && <div>Publication receipt {receipt.publicationId}</div>}
                {receipt?.publicationStatus && <div>Publication status: {readableCode(receipt.publicationStatus)}</div>}
                {receipt?.syncStatus && <div>Synchronization status: {readableCode(receipt.syncStatus)}</div>}
                {receipt?.syncStatus === 'pending' && (
                    <Message severity="warn" text="Semantic synchronization pending. Search availability is not yet confirmed." />
                )}
            </div>
        </Card>
    );
}
