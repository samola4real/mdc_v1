import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { ProgressSpinner } from 'primereact/progressspinner';
import { getCatalogFilters } from '@/services/mdc/catalog.service';
import {
    getDemoBackendStatus,
    getProviderDemoState,
    regenerateRdf,
    reloadFuseki,
    runFusekiSmokeTest
} from '@/services/mdc/demoAdmin.service';
import { getBackendHealth, getDemoHealth } from '@/services/mdc/health.service';
import StatusTag from './StatusTag';

const LABELS = {
    fuseki_with_h5_policy: 'Fuseki',
    local_rdflib_with_h5_policy: 'RDFLib',
    harmonized_yaml_h5_matcher: 'Harmonized YAML',
    demo_only_not_marketplace_contract: 'Demo only - not Marketplace contract'
};

const initialRequestState = {
    backendHealth: { data: null, error: null },
    demoHealth: { data: null, error: null },
    backendStatus: { data: null, error: null },
    providerState: { data: null, error: null },
    catalogFilters: { data: null, error: null }
};

const toArray = (value) => {
    if (Array.isArray(value)) return value;
    if (value && typeof value === 'object') return Object.values(value);
    return value == null || value === '' ? [] : [value];
};

const firstValue = (...values) => values.find((value) => value !== undefined && value !== null && value !== '');

const getCollectionCount = (value) => {
    if (Array.isArray(value)) return value.length;
    if (value && typeof value === 'object') return Object.keys(value).length;
    return value ? 1 : 0;
};

const displayValue = (value) => {
    const nextValue = firstValue(value, 'Not reported');
    if (typeof nextValue === 'boolean') return nextValue ? 'Yes' : 'No';
    if (Array.isArray(nextValue)) return nextValue.map(displayValue).join(', ') || 'Not reported';
    if (typeof nextValue === 'object') return 'Reported';
    return LABELS[nextValue] || String(nextValue);
};

const isHealthyResponse = (data) => {
    if (!data) return true;
    const rawStatus = String(data.status || data.health || data.state || '').toLowerCase();
    return !['error', 'failed', 'unhealthy', 'down', 'unavailable'].includes(rawStatus);
};

const getErrorMessage = (error, fallback = 'Endpoint unavailable.') => {
    if (!error) return null;
    if (error.status === 404) return 'Endpoint unavailable or demo API is disabled.';
    return error.message || fallback;
};

const toResultState = (result) => {
    if (result.status === 'fulfilled') {
        return { data: result.value, error: null };
    }
    return { data: null, error: result.reason };
};

const getProviderEntries = (state) => {
    const providers = firstValue(
        state?.providers,
        state?.state?.providers,
        state?.demo_state?.providers,
        state?.data?.providers
    );

    return toArray(providers);
};

const getProviderPayload = (entry) => entry?.payload || entry?.provider || entry;

const buildProviderRows = (state) => getProviderEntries(state).map((entry, index) => {
    const provider = getProviderPayload(entry);
    const providerId = firstValue(
        provider?.provider_id,
        provider?.providerId,
        provider?.id,
        entry?.provider_id,
        entry?.id,
        `provider-${index + 1}`
    );
    const providerName = firstValue(
        provider?.provider_name,
        provider?.providerName,
        provider?.name,
        providerId
    );

    return {
        id: String(providerId),
        providerId: String(providerId),
        providerName: String(providerName),
        offeringsCount: toArray(provider?.offerings).length
    };
});

const getProviderStateSummary = (state) => {
    const providerRows = buildProviderRows(state);
    const updates = firstValue(
        state?.updates,
        state?.provider_updates,
        state?.saved_updates,
        state?.state?.updates,
        state?.demo_state?.updates,
        state?.data?.updates
    );
    const lastUpdated = firstValue(
        state?.last_updated,
        state?.lastUpdated,
        state?.updated_at,
        state?.updatedAt,
        state?.timestamp,
        state?.state?.last_updated,
        state?.demo_state?.last_updated,
        state?.data?.last_updated
    );

    return {
        providerRows,
        providersCount: providerRows.length,
        updatesCount: getCollectionCount(updates),
        lastUpdated: lastUpdated ? String(lastUpdated) : 'Not reported'
    };
};

const getCatalogRoot = (data) => data?.filters || data?.data?.filters || data?.data || data || {};

const getCatalogSummary = (data) => {
    const filters = getCatalogRoot(data);

    return {
        available: Boolean(data),
        materialsCount: getCollectionCount(firstValue(filters.materials, filters.material)),
        processesCount: getCollectionCount(firstValue(filters.processes, filters.process)),
        certificationsCount: getCollectionCount(firstValue(filters.certifications, filters.certification)),
        partFamiliesCount: getCollectionCount(firstValue(filters.part_families, filters.partFamilies, filters.families))
    };
};

const formatJson = (value) => JSON.stringify(value, null, 2);

const StatusCard = ({ title, value, status, statusLabel, description }) => (
    <Card
        title={title}
        className="h-full"
        style={{ borderTop: '3px solid var(--blue)', background: 'var(--bg-card)' }}
    >
        <div className="flex align-items-start justify-content-between gap-3">
            <div>
                <p className="text-xl font-semibold text-900 mt-0 mb-2">{value}</p>
                {description ? <p className="text-600 line-height-3 mb-0">{description}</p> : null}
            </div>
            <StatusTag value={statusLabel} status={status} />
        </div>
    </Card>
);

const JsonDetails = ({ header, value }) => {
    if (!value) return null;

    return (
        <Panel header={header} toggleable collapsed className="mt-3">
            <pre className="m-0 p-3 surface-100 border-round text-sm overflow-auto">
                {formatJson(value)}
            </pre>
        </Panel>
    );
};

const AdminAuditPanel = () => {
    const [requests, setRequests] = useState(initialRequestState);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(null);
    const [actionState, setActionState] = useState({
        name: null,
        loading: false,
        result: null,
        error: null
    });

    const loadAdminState = useCallback(async () => {
        setLoading(true);
        const [backendHealth, demoHealth, backendStatus, providerState, catalogFilters] = await Promise.allSettled([
            getBackendHealth(),
            getDemoHealth(),
            getDemoBackendStatus(),
            getProviderDemoState(),
            getCatalogFilters()
        ]);

        setRequests({
            backendHealth: toResultState(backendHealth),
            demoHealth: toResultState(demoHealth),
            backendStatus: toResultState(backendStatus),
            providerState: toResultState(providerState),
            catalogFilters: toResultState(catalogFilters)
        });
        setLastUpdated(new Date());
        setLoading(false);
    }, []);

    useEffect(() => {
        loadAdminState();
    }, [loadAdminState]);

    const providerSummary = useMemo(
        () => getProviderStateSummary(requests.providerState.data),
        [requests.providerState.data]
    );
    const catalogSummary = useMemo(
        () => getCatalogSummary(requests.catalogFilters.data),
        [requests.catalogFilters.data]
    );

    const systemCards = useMemo(() => {
        const backendHealthy = !requests.backendHealth.error && isHealthyResponse(requests.backendHealth.data);
        const demoHealthy = !requests.demoHealth.error && isHealthyResponse(requests.demoHealth.data);
        const backendStatus = requests.backendStatus.data || {};
        const backendStatusAvailable = !requests.backendStatus.error && Boolean(requests.backendStatus.data);

        return [
            {
                title: 'Backend API',
                value: backendHealthy ? 'Available' : 'Unavailable',
                status: backendHealthy ? 'healthy' : 'unavailable',
                statusLabel: backendHealthy ? 'Healthy' : 'Unavailable',
                description: backendHealthy
                    ? 'Shared backend health endpoint responded.'
                    : getErrorMessage(requests.backendHealth.error, 'Backend API health could not be loaded.')
            },
            {
                title: 'Demo API',
                value: demoHealthy ? 'Available' : 'Unavailable',
                status: demoHealthy ? 'enabled' : 'unavailable',
                statusLabel: demoHealthy ? 'Demo enabled' : 'Unavailable',
                description: demoHealthy
                    ? 'Demo health endpoint responded.'
                    : getErrorMessage(requests.demoHealth.error, 'Demo API health could not be loaded.')
            },
            {
                title: 'Service discovery backend',
                value: backendStatusAvailable ? displayValue(backendStatus.active_backend) : 'Unavailable',
                status: backendStatusAvailable ? 'online' : 'unavailable',
                statusLabel: backendStatusAvailable ? 'Reported' : 'Unavailable',
                description: backendStatusAvailable
                    ? 'Reported by the demo backend-status endpoint.'
                    : getErrorMessage(requests.backendStatus.error, 'Backend status endpoint did not respond.')
            },
            {
                title: 'Fuseki dataset/status',
                value: backendStatusAvailable
                    ? displayValue(firstValue(backendStatus.fuseki_dataset, backendStatus.fuseki_status))
                    : 'Unavailable',
                status: backendStatusAvailable ? 'info' : 'unavailable',
                statusLabel: backendStatusAvailable ? 'Reported' : 'Unavailable',
                description: backendStatusAvailable
                    ? 'Dataset/status reported by the demo backend, when available.'
                    : 'No static Fuseki dataset is shown without a backend response.'
            },
            {
                title: 'Fallback backend',
                value: backendStatusAvailable ? displayValue(backendStatus.fallback_backends) : 'Unavailable',
                status: backendStatusAvailable ? 'info' : 'unavailable',
                statusLabel: backendStatusAvailable ? 'Reported' : 'Unavailable',
                description: backendStatusAvailable
                    ? 'Fallback directions reported by the backend-status endpoint.'
                    : 'No fallback backend is shown as live when the endpoint is unavailable.'
            },
            {
                title: 'Demo namespace',
                value: backendStatusAvailable
                    ? displayValue(firstValue(backendStatus.demo_namespace, backendStatus.demo_api_namespace))
                    : 'Unavailable',
                status: backendStatusAvailable ? 'demo-only' : 'unavailable',
                statusLabel: backendStatusAvailable ? 'Demo-only' : 'Unavailable',
                description: backendStatusAvailable
                    ? 'Demo-only endpoint namespace used by the MDC demo backend.'
                    : 'Namespace is not inferred as live without backend status.'
            }
        ];
    }, [requests]);

    const providerCards = [
        {
            title: 'Registered demo providers',
            value: String(providerSummary.providersCount),
            status: requests.providerState.error ? 'unavailable' : 'info',
            statusLabel: requests.providerState.error ? 'Unavailable' : 'Loaded',
            description: requests.providerState.error
                ? getErrorMessage(requests.providerState.error, 'Provider demo state could not be loaded.')
                : 'Count parsed from the demo provider state endpoint.'
        },
        {
            title: 'Demo provider updates',
            value: String(providerSummary.updatesCount),
            status: requests.providerState.error ? 'unavailable' : 'info',
            statusLabel: requests.providerState.error ? 'Unavailable' : 'Loaded',
            description: 'Update count is shown when the demo state response contains update entries.'
        },
        {
            title: 'Last updated',
            value: providerSummary.lastUpdated,
            status: requests.providerState.error ? 'unavailable' : 'info',
            statusLabel: requests.providerState.error ? 'Unavailable' : 'Reported',
            description: 'Timestamp from the demo state response, if provided.'
        }
    ];

    const catalogCards = [
        {
            title: 'Catalogue filters',
            value: catalogSummary.available && !requests.catalogFilters.error ? 'Available' : 'Unavailable',
            status: catalogSummary.available && !requests.catalogFilters.error ? 'success' : 'unavailable',
            statusLabel: catalogSummary.available && !requests.catalogFilters.error ? 'Available' : 'Unavailable',
            description: requests.catalogFilters.error
                ? getErrorMessage(requests.catalogFilters.error, 'Catalogue filters could not be loaded.')
                : 'Filter payload loaded from the shared catalogue endpoint.'
        },
        {
            title: 'Materials',
            value: String(catalogSummary.materialsCount),
            status: requests.catalogFilters.error ? 'unavailable' : 'info',
            statusLabel: 'Count',
            description: 'Available material filter values.'
        },
        {
            title: 'Processes',
            value: String(catalogSummary.processesCount),
            status: requests.catalogFilters.error ? 'unavailable' : 'info',
            statusLabel: 'Count',
            description: 'Available process filter values.'
        },
        {
            title: 'Certifications',
            value: String(catalogSummary.certificationsCount),
            status: requests.catalogFilters.error ? 'unavailable' : 'info',
            statusLabel: 'Count',
            description: 'Available certification filter values.'
        },
        {
            title: 'Part families',
            value: String(catalogSummary.partFamiliesCount),
            status: requests.catalogFilters.error ? 'unavailable' : 'info',
            statusLabel: 'Count',
            description: 'Available part family filter values, if reported.'
        }
    ];

    const runAction = async ({ name, action, confirmMessage }) => {
        if (confirmMessage && !window.confirm(confirmMessage)) {
            return;
        }

        setActionState({ name, loading: true, result: null, error: null });

        try {
            const result = await action();
            setActionState({ name, loading: false, result, error: null });
            if (name !== 'Run Fuseki Smoke Test') {
                loadAdminState();
            }
        } catch (error) {
            setActionState({ name, loading: false, result: null, error });
        }
    };

    const actionLoading = (name) => actionState.loading && actionState.name === name;

    return (
        <div className="flex flex-column gap-4">
            <Message
                severity="info"
                text="Demo Admin Console uses demo-only status and technical endpoints. It does not expose production provider publication controls."
                className="w-full justify-content-start"
            />

            <Panel header="System status">
                <div className="flex flex-column md:flex-row md:align-items-center md:justify-content-between gap-3 mb-3">
                    <p className="text-600 line-height-3 my-0">
                        Live status from backend health, demo health, and service-discovery backend-status endpoints.
                    </p>
                    <div className="flex align-items-center gap-3">
                        {lastUpdated ? <span className="text-sm text-600">Last refreshed: {lastUpdated.toLocaleTimeString()}</span> : null}
                        <Button label="Refresh" icon="pi pi-refresh" onClick={loadAdminState} loading={loading} outlined />
                    </div>
                </div>

                {loading ? (
                    <div className="flex align-items-center gap-3 surface-100 border-round p-3 mb-3">
                        <ProgressSpinner style={{ width: '2rem', height: '2rem' }} strokeWidth="4" />
                        <span className="text-700">Loading demo admin status...</span>
                    </div>
                ) : null}

                <div className="grid">
                    {systemCards.map((card) => (
                        <div key={card.title} className="col-12 md:col-6 xl:col-4">
                            <StatusCard {...card} />
                        </div>
                    ))}
                </div>
            </Panel>

            <Panel header="Demo provider state">
                <div className="grid">
                    {providerCards.map((card) => (
                        <div key={card.title} className="col-12 md:col-4">
                            <StatusCard {...card} />
                        </div>
                    ))}
                </div>

                {providerSummary.providerRows.length > 0 ? (
                    <div className="mt-3">
                        <DataTable value={providerSummary.providerRows} dataKey="id" responsiveLayout="scroll" stripedRows>
                            <Column field="providerName" header="Provider name" sortable />
                            <Column field="providerId" header="Provider ID" sortable />
                            <Column field="offeringsCount" header="Offerings" sortable />
                        </DataTable>
                    </div>
                ) : (
                    <Message
                        severity={requests.providerState.error ? 'warn' : 'info'}
                        text={requests.providerState.error ? 'Demo provider state is unavailable.' : 'No registered demo providers were reported.'}
                        className="w-full justify-content-start mt-3"
                    />
                )}

                <JsonDetails header="Advanced provider state response" value={requests.providerState.data} />
            </Panel>

            <Panel header="Catalogue/search readiness">
                <p className="text-600 line-height-3 mt-0">
                    Catalogue readiness is based on the existing catalogue filters endpoint. No search test endpoint is called from Admin.
                </p>
                <div className="grid">
                    {catalogCards.map((card) => (
                        <div key={card.title} className="col-12 md:col-6 xl:col-4">
                            <StatusCard {...card} />
                        </div>
                    ))}
                </div>
                <JsonDetails header="Advanced catalogue filter response" value={requests.catalogFilters.data} />
            </Panel>

            <Panel header="Technical actions">
                <Message
                    severity="warn"
                    text="Demo-only technical action area. RDF regeneration and Fuseki reload can change demo runtime state and require confirmation."
                    className="w-full justify-content-start mb-3"
                />
                <div className="flex flex-wrap gap-2">
                    <Button
                        label="Run Fuseki Smoke Test"
                        icon="pi pi-database"
                        onClick={() => runAction({ name: 'Run Fuseki Smoke Test', action: runFusekiSmokeTest })}
                        loading={actionLoading('Run Fuseki Smoke Test')}
                    />
                    <Button
                        label="Regenerate RDF"
                        icon="pi pi-refresh"
                        outlined
                        onClick={() => runAction({
                            name: 'Regenerate RDF',
                            action: regenerateRdf,
                            confirmMessage: 'Regenerate demo RDF now? This is a demo-only technical action.'
                        })}
                        loading={actionLoading('Regenerate RDF')}
                    />
                    <Button
                        label="Reload Fuseki"
                        icon="pi pi-sync"
                        outlined
                        onClick={() => runAction({
                            name: 'Reload Fuseki',
                            action: reloadFuseki,
                            confirmMessage: 'Reload the demo Fuseki dataset now? This is a demo-only technical action.'
                        })}
                        loading={actionLoading('Reload Fuseki')}
                    />
                </div>

                {actionState.error ? (
                    <Message
                        severity="error"
                        text={`${actionState.name} failed: ${getErrorMessage(actionState.error, 'Action failed.')}`}
                        className="w-full justify-content-start mt-3"
                    />
                ) : null}
                {actionState.result ? (
                    <Message
                        severity="success"
                        text={`${actionState.name} completed successfully.`}
                        className="w-full justify-content-start mt-3"
                    />
                ) : null}
                <JsonDetails header="Last technical action response" value={actionState.result || actionState.error} />
            </Panel>
        </div>
    );
};

export default AdminAuditPanel;
