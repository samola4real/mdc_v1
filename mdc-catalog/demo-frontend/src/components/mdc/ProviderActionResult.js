import React from 'react';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { Tag } from 'primereact/tag';

const errorDetails = {
    400: 'Review the rejected fields and submit a valid payload.',
    401: 'Sign in with MaaSAI Keycloak.',
    403: 'Check your verified role and the disposable ID scope.',
    404: 'The requested resource is absent.',
    409: 'Load the existing record before deciding what to change.',
    412: 'A newer revision exists. Reload the resource and review your changes.',
    428: 'Load the resource again to get its current strong ETag.',
    503: 'Service or publication is unavailable. Read the resource and receipt before retrying a write.'
};

const ProviderActionResult = ({ result }) => {
    if (!result) return null;
    const { action, response, error } = result;
    const publicationId = response?.publication_id || error?.publicationId;
    const publicationStatus = response?.publication_status || error?.publicationStatus;
    const syncStatus = response?.sync_status || error?.syncStatus;
    const success = publicationId ? action + ' accepted' : action + ' completed';
    const description = error && (errorDetails[error.status] || (error.status == null || error.status >= 500
        ? 'Check current state before retrying a write.' : ''));
    const message = error ? [action + ' failed.', error.message, description].filter(Boolean).join(' ') : success;

    return (
        <Card>
            <div className="flex flex-column gap-3">
                <Message severity={error ? 'error' : 'success'} text={message} className="w-full justify-content-start" />
                {publicationId && (
                    <div className="flex gap-2 flex-wrap align-items-center">
                        <span>Publication {publicationId}</span>
                        {publicationStatus && <Tag value={publicationStatus} severity={syncStatus === 'pending' ? 'warning' : 'info'} />}
                        {syncStatus === 'pending' && <span>Semantic synchronization pending</span>}
                    </div>
                )}
                {(response || error?.details) && (
                    <Panel header="MDC response details" toggleable collapsed>
                        <pre className="m-0 white-space-pre-wrap">{JSON.stringify(response || error.details, null, 2)}</pre>
                    </Panel>
                )}
            </div>
        </Card>
    );
};

export default ProviderActionResult;
