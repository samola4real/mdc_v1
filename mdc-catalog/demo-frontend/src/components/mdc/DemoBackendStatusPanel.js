import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { ProgressSpinner } from 'primereact/progressspinner';
import { getBackendHealth, getDemoHealth } from '@/services/mdc/health.service';
import { getDemoBackendStatus } from '@/services/mdc/demoAdmin.service';
import DemoStatusCards from './DemoStatusCards';

const LABELS = {
    fuseki_with_h5_policy: 'Fuseki + H5 policy',
    local_rdflib_with_h5_policy: 'RDFLib + H5 policy',
    harmonized_yaml_h5_matcher: 'Harmonized YAML + H5 matcher',
    demo_only_not_marketplace_contract: 'Demo only - not Marketplace contract'
};

const fallbackBackendStatus = {
    active_backend: 'fuseki_with_h5_policy',
    fallback_backends: ['local_rdflib_with_h5_policy', 'harmonized_yaml_h5_matcher'],
    fuseki_dataset: 'mdc-service-discovery',
    marketplace_shared_api_unchanged: true,
    endpoint_activation_status: 'demo_only_not_marketplace_contract'
};

const displayValue = (value) => {
    if (value == null || value === '') {
        return 'Not reported';
    }
    if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
    }
    return LABELS[value] || String(value);
};

const displayList = (values) => {
    if (!Array.isArray(values) || values.length === 0) {
        return 'Not reported';
    }
    return values.map(displayValue).join(', ');
};

const isHealthyResponse = (data) => {
    if (!data) return true;
    const rawStatus = String(data.status || data.health || data.state || '').toLowerCase();
    return !['error', 'failed', 'unhealthy', 'down'].includes(rawStatus);
};

const getErrorMessage = (key, error) => {
    if (key === 'backendHealth') {
        return 'Backend API unavailable. Check the configured MDC API URL, backend availability, HTTPS, and CORS settings.';
    }

    if (error?.status === 404) {
        return 'Demo API is disabled or not available. Enable MDC_DEMO_API_ENABLED=true in the backend for demo endpoints.';
    }

    return error?.message || 'Status endpoint unavailable.';
};

const toResultState = (result) => {
    if (result.status === 'fulfilled') {
        return { data: result.value, error: null };
    }
    return { data: null, error: result.reason };
};

const DemoBackendStatusPanel = () => {
    const [status, setStatus] = useState({
        backendHealth: { data: null, error: null },
        demoHealth: { data: null, error: null },
        backendStatus: { data: null, error: null }
    });
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(null);

    const loadStatus = useCallback(async () => {
        setLoading(true);
        const [backendHealth, demoHealth, backendStatus] = await Promise.allSettled([
            getBackendHealth(),
            getDemoHealth(),
            getDemoBackendStatus()
        ]);

        setStatus({
            backendHealth: toResultState(backendHealth),
            demoHealth: toResultState(demoHealth),
            backendStatus: toResultState(backendStatus)
        });
        setLastUpdated(new Date());
        setLoading(false);
    }, []);

    useEffect(() => {
        loadStatus();
    }, [loadStatus]);

    const cards = useMemo(() => {
        const backendStatus = status.backendStatus.data || fallbackBackendStatus;
        const sharedOk = !status.backendHealth.error && isHealthyResponse(status.backendHealth.data);
        const demoOk = !status.demoHealth.error && isHealthyResponse(status.demoHealth.data);
        const backendStatusOk = !status.backendStatus.error;
        const demoEnabled = status.demoHealth.data?.demo_api_enabled ?? backendStatus.demo_api_enabled;

        return [
            {
                label: 'Backend API health',
                value: sharedOk ? 'Healthy / Online' : 'Unavailable',
                status: sharedOk ? 'healthy' : 'unavailable',
                statusLabel: sharedOk ? 'Healthy' : 'Unavailable',
                description: sharedOk
                    ? 'Shared Marketplace-like health endpoint responded.'
                    : getErrorMessage('backendHealth', status.backendHealth.error)
            },
            {
                label: 'Demo API health',
                value: demoOk ? 'Demo enabled' : 'Unavailable',
                status: demoOk ? 'enabled' : 'unavailable',
                statusLabel: demoOk ? 'Demo enabled' : 'Unavailable',
                description: demoOk
                    ? 'Demo health endpoint responded under /api/demo.'
                    : getErrorMessage('demoHealth', status.demoHealth.error)
            },
            {
                label: 'Demo-reported backend direction',
                value: displayValue(backendStatus.active_backend),
                status: backendStatusOk ? 'info' : 'warning',
                statusLabel: backendStatusOk ? 'Demo metadata' : 'Fallback',
                description: backendStatusOk
                    ? 'Illustrative metadata; this does not verify the live discovery runtime.'
                    : 'Fallback label shown until demo backend status is available.'
            },
            {
                label: 'Fallback backends',
                value: displayList(backendStatus.fallback_backends),
                status: backendStatusOk ? 'info' : 'warning',
                statusLabel: backendStatusOk ? 'Reported' : 'Fallback',
                description: backendStatusOk
                    ? 'Illustrative fallback directions reported by the demo endpoint.'
                    : 'Static fallback directions from the F1 shell are shown.'
            },
            {
                label: 'Fuseki dataset',
                value: displayValue(backendStatus.fuseki_dataset),
                status: backendStatusOk ? 'info' : 'warning',
                statusLabel: backendStatusOk ? 'Reported' : 'Fallback',
                description: 'Demo-reported label only; the frontend does not directly verify or access Fuseki.'
            },
            {
                label: 'Marketplace/shared API unchanged',
                value: displayValue(backendStatus.marketplace_shared_api_unchanged),
                status: backendStatus.marketplace_shared_api_unchanged === false ? 'warning' : 'success',
                statusLabel: backendStatus.marketplace_shared_api_unchanged === false ? 'Review' : 'Unchanged',
                description: 'Demo-only controls remain separate from Marketplace-facing endpoints.'
            },
            {
                label: 'Endpoint activation status',
                value: displayValue(backendStatus.endpoint_activation_status),
                status: 'demo-only',
                statusLabel: 'Demo-only',
                description: demoEnabled === false
                    ? 'Demo status reports that demo API is not enabled.'
                    : 'Demo endpoints are expected under the configured /api/demo namespace.'
            },
            {
                label: 'Demo API namespace',
                value: '/api/demo/',
                status: 'demo-only',
                statusLabel: 'Demo-only',
                description: 'F3 reads status only and does not call admin mutation endpoints.'
            }
        ];
    }, [status]);

    const errors = [
        status.backendHealth.error ? getErrorMessage('backendHealth', status.backendHealth.error) : null,
        status.demoHealth.error ? getErrorMessage('demoHealth', status.demoHealth.error) : null,
        status.backendStatus.error ? getErrorMessage('backendStatus', status.backendStatus.error) : null
    ].filter(Boolean);

    return (
        <Panel header="Backend health and demo-reported metadata">
            <div className="flex flex-column md:flex-row md:align-items-center md:justify-content-between gap-3 mb-3">
                <div>
                    <p className="text-600 line-height-3 my-0">
                        Read-only health responses plus illustrative labels from demo backend-status. The labels are not live Fuseki/runtime verification.
                    </p>
                    {lastUpdated ? (
                        <div className="text-sm text-600 mt-2">
                            Last refreshed: {lastUpdated.toLocaleTimeString()}
                        </div>
                    ) : null}
                </div>
                <Button
                    label="Refresh status"
                    icon="pi pi-refresh"
                    onClick={loadStatus}
                    loading={loading}
                    outlined
                />
            </div>

            {loading ? (
                <div className="flex align-items-center gap-3 surface-100 border-round p-3 mb-3">
                    <ProgressSpinner style={{ width: '2rem', height: '2rem' }} strokeWidth="4" />
                    <span className="text-700">Loading backend status...</span>
                </div>
            ) : null}

            {errors.length > 0 ? (
                <div className="flex flex-column gap-2 mb-3">
                    {errors.map((message) => (
                        <Message
                            key={message}
                            severity="warn"
                            text={message}
                            className="w-full justify-content-start"
                        />
                    ))}
                </div>
            ) : (
                <Message
                    severity="success"
                    text="All F3 status endpoints responded successfully."
                    className="w-full justify-content-start mb-3"
                />
            )}

            <DemoStatusCards cards={cards} />
        </Panel>
    );
};

export default DemoBackendStatusPanel;
