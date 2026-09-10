import React from 'react';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { Tag } from 'primereact/tag';

const stringifyDetail = (value) => {
    if (!value) {
        return '';
    }

    if (typeof value === 'string') {
        return value;
    }

    if (Array.isArray(value)) {
        return value.map(stringifyDetail).filter(Boolean).join(' ');
    }

    if (typeof value === 'object') {
        const directMessage = value.message || value.detail || value.error || value.non_field_errors;

        if (directMessage) {
            return stringifyDetail(directMessage);
        }

        return Object.entries(value)
            .map(([key, item]) => {
                const next = stringifyDetail(item);
                return next ? `${key}: ${next}` : '';
            })
            .filter(Boolean)
            .join(' ');
    }

    return String(value);
};

const getBackendMessage = (error) => stringifyDetail(error?.details) || error?.message || '';
const isEndpointUnavailable = (error) => (
    error?.status === 404 ||
    (error?.status == null && Boolean(error?.message || error?.details))
);

const getResultCopy = (result) => {
    if (!result) {
        return null;
    }

    if (!result.error) {
        if (result.action === 'save' && result.payloadAction === 'register_provider') {
            return {
                severity: 'success',
                title: 'Provider registered for demo',
                detail: ''
            };
        }

        if (result.action === 'save') {
            return {
                severity: 'success',
                title: 'Provider update saved for demo',
                detail: ''
            };
        }

        return {
            severity: 'success',
            title: 'Preview successful',
            detail: ''
        };
    }

    if (result.error?.status === 501) {
        return {
            severity: 'warn',
            title: 'Backend demo action not implemented yet',
            detail: 'This UI is ready, but the backend demo provider action is reserved for a later phase.'
        };
    }

    if (isEndpointUnavailable(result.error)) {
        return {
            severity: 'warn',
            title: 'Demo provider endpoint unavailable',
            detail: 'Check that Django is running and the demo API is available.'
        };
    }

    if (result.error?.status === 400) {
        return {
            severity: 'error',
            title: 'Provider payload was rejected.',
            detail: ''
        };
    }

    if (result.error?.status >= 500) {
        return {
            severity: 'error',
            title: 'Backend error while processing provider demo request.',
            detail: ''
        };
    }

    if (result.error) {
        const backendMessage = getBackendMessage(result.error);

        return {
            severity: 'error',
            title: 'Provider demo action failed',
            detail: backendMessage || 'The backend returned an error.'
        };
    }
};

const getOfferings = (payload) => payload?.offerings?.map((item) => item.offering_name).join(', ') || 'Not provided';
const getMessageText = (copy) => copy.detail ? `${copy.title}. ${copy.detail}` : copy.title;

const ProviderActionResult = ({ result, payload }) => {
    const copy = getResultCopy(result);

    if (!copy) {
        return null;
    }

    return (
        <Card>
            <div className="flex flex-column gap-3">
                <Message severity={copy.severity} text={getMessageText(copy)} className="w-full justify-content-start" />
                {!result.error ? (
                    <div className="grid">
                        <div className="col-12 md:col-4">
                            <div className="text-sm text-600">Provider</div>
                            <div className="font-semibold text-900">{payload.provider_name}</div>
                        </div>
                        <div className="col-12 md:col-4">
                            <div className="text-sm text-600">Offering</div>
                            <div className="font-semibold text-900">{getOfferings(payload)}</div>
                        </div>
                        <div className="col-12 md:col-4">
                            <div className="text-sm text-600">Status</div>
                            <Tag
                                value={result.action === 'save' ? 'Saved to demo state' : 'Valid demo preview'}
                                severity="success"
                                rounded
                            />
                        </div>
                    </div>
                ) : null}
                <Panel header="Advanced/debug response JSON" toggleable collapsed>
                    <pre className="m-0 white-space-pre-wrap">{JSON.stringify(result.response || result.error?.details || result.error, null, 2)}</pre>
                </Panel>
            </div>
        </Card>
    );
};

export default ProviderActionResult;
