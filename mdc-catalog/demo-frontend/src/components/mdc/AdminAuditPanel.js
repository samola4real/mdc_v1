import React, { useCallback, useEffect, useState } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { getCatalogFilters, normalizeCatalogFilters } from '@/services/mdc/catalog.service';
import { getBackendHealth } from '@/services/mdc/health.service';
import StatusTag from './StatusTag';

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
                {JSON.stringify(value, null, 2)}
            </pre>
        </Panel>
    );
};

const AdminAuditPanel = () => {
    const [checks, setChecks] = useState(null);
    const [loading, setLoading] = useState(true);
    const refresh = useCallback(async () => {
        setLoading(true);
        const results = await Promise.allSettled([
            getBackendHealth(),
            getCatalogFilters().then((data) => ({ data, filters: normalizeCatalogFilters(data) }))
        ]);
        setChecks(results);
        setLoading(false);
    }, []);
    useEffect(() => { refresh(); }, [refresh]);

    const [health, catalogue] = checks || [];
    const healthy = health?.value?.status === 'ok';
    const filters = catalogue?.value?.filters;

    return (
        <div className="flex flex-column gap-4">
            <Panel header="System status">
                <div className="grid">
                    <div className="col-12 md:col-6">
                        <StatusCard title="Backend API" value={healthy ? 'Available' : loading ? 'Checking' : 'Unavailable'}
                            status={healthy ? 'healthy' : 'unavailable'} statusLabel={healthy ? 'Live' : 'Not confirmed'}
                            description={health?.reason?.message || 'Shared API liveness.'} />
                    </div>
                    <div className="col-12 md:col-6">
                        <StatusCard title="Catalogue filters" value={filters ? 'Loaded' : loading ? 'Checking' : 'Unavailable'}
                            status={filters ? 'ready' : 'unavailable'} statusLabel={filters ? 'Available' : 'Not confirmed'}
                            description={catalogue?.reason?.message || 'Current values from the accepted MDC Preview.'} />
                    </div>
                </div>
                <Button label="Refresh checks" icon="pi pi-refresh" outlined loading={loading} disabled={loading} onClick={refresh} />
                <JsonDetails header="Health response" value={health?.value} />
            </Panel>
            <Panel header="Catalogue/search readiness">
                {filters ? (
                    <p className="m-0">{filters.partFamilies.length} part families, {filters.materials.length} materials,
                        {' '}{filters.processes.length} processes, and {filters.certifications.length} certifications.</p>
                ) : <Message severity="warn" text="Current catalogue vocabulary is unavailable." />}
                <JsonDetails header="Catalogue filter response" value={catalogue?.value?.data} />
            </Panel>
        </div>
    );
};

export default AdminAuditPanel;
