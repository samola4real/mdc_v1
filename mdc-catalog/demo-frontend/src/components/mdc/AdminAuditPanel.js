import React, { useEffect, useState } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Panel } from 'primereact/panel';
import { getCatalogFilters, normalizeCatalogFilters } from '@/services/mdc/catalog.service';
import { getBackendHealth } from '@/services/mdc/health.service';
import AdminProviderDeletion from './AdminProviderDeletion';
import { readAdminAvailability } from './adminDashboardFlow';
import StatusTag from './StatusTag';

const availabilityServices = { getBackendHealth, getCatalogFilters, normalizeCatalogFilters };
const availabilityLabels = {
    checking: 'Checking',
    available: 'Available',
    unavailable: 'Unavailable',
    error: 'Check failed'
};

const AvailabilityCard = ({ title, status }) => (
    <Card className="h-full" style={{ borderTop: '3px solid var(--blue)' }}
        pt={{ body: { className: 'p-3' }, content: { className: 'p-0' } }}>
        <div className="flex flex-wrap align-items-center justify-content-between gap-2">
            <h2 className="text-base font-semibold m-0">{title}</h2>
            <StatusTag value={availabilityLabels[status]} status={status === 'available' ? 'healthy' : status} />
        </div>
    </Card>
);

const AdminAuditPanel = () => {
    const [checks, setChecks] = useState(null);
    const [checkAttempt, setCheckAttempt] = useState(0);
    const loading = checks === null;

    useEffect(() => {
        let active = true;
        readAdminAvailability(availabilityServices).then((result) => { if (active) setChecks(result); });
        return () => { active = false; };
    }, [checkAttempt]);

    const refresh = () => {
        setChecks(null);
        setCheckAttempt((attempt) => attempt + 1);
    };

    return (
        <div className="flex flex-column gap-4">
            <div className="flex flex-column sm:flex-row gap-3" role="group" aria-label="System availability" aria-live="polite">
                <div className="flex-1">
                    <AvailabilityCard title="Backend API" status={checks?.apiStatus ?? 'checking'} />
                </div>
                <div className="flex-1">
                    <AvailabilityCard title="Catalogue" status={checks?.catalogueStatus ?? 'checking'} />
                </div>
            </div>
            <AdminProviderDeletion />
            <Panel header="Catalogue overview">
                {checks?.counts ? (
                    <dl className="grid m-0 mb-2">
                        {Object.entries(checks.counts).map(([label, count]) => (
                            <div className="col-6 md:col-3" key={label}>
                                <dt className="text-sm">{label}</dt>
                                <dd className="m-0 text-2xl font-semibold">{count}</dd>
                            </div>
                        ))}
                    </dl>
                ) : <p className="mt-0">{loading ? 'Checking catalogue…' : 'Catalogue counts are unavailable.'}</p>}
                <Button type="button" label="Refresh checks" icon="pi pi-refresh" outlined
                    loading={loading} disabled={loading} onClick={refresh} />
            </Panel>
        </div>
    );
};

export default AdminAuditPanel;
