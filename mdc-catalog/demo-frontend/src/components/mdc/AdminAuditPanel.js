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

const backendDescriptions = {
    checking: 'Checking service availability.',
    available: 'The catalogue API is responding.',
    unavailable: 'The API reported an unavailable state.',
    error: 'The health check could not be completed.'
};
const catalogueDescriptions = {
    checking: 'Waiting for catalogue filters.',
    available: 'The current catalogue filters are loaded.',
    unavailable: 'The catalogue filters are unavailable.',
    error: 'The catalogue filters could not be loaded.'
};
const metricIcons = { 'Part families': 'pi-box', Materials: 'pi-clone', Processes: 'pi-cog', Certifications: 'pi-verified' };

const AvailabilityCard = ({ title, icon, status, descriptions }) => (
    <Card className="mdc-admin-availability-card">
        <div className="mdc-admin-availability-card__content">
            <span className="mdc-admin-icon"><i className={'pi ' + icon} aria-hidden="true" /></span>
            <div className="mdc-admin-availability-card__description">
                <h2>{title}</h2>
                <p>{descriptions[status]}</p>
            </div>
            <span className={'mdc-admin-status mdc-admin-status--' + status}>
                <StatusTag value={availabilityLabels[status]} status={status === 'available' ? 'healthy' : status} />
            </span>
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
        <>
            <div className="mdc-admin-availability" role="group" aria-label="System availability" aria-live="polite">
                <AvailabilityCard title="Backend API" icon="pi-server" status={checks?.apiStatus ?? 'checking'} descriptions={backendDescriptions} />
                <AvailabilityCard title="Catalogue" icon="pi-database" status={checks?.catalogueStatus ?? 'checking'} descriptions={catalogueDescriptions} />
            </div>
            <AdminProviderDeletion filters={checks?.filters} />
            <Panel className="mdc-admin-section" header={<><i className="pi pi-chart-bar" aria-hidden="true" />Catalogue overview</>}
                pt={{ title: { role: 'heading', 'aria-level': 2 } }}>
                {checks?.counts ? (
                    <dl className="mdc-admin-metrics">
                        {Object.entries(checks.counts).map(([label, count]) => (
                            <div className="mdc-admin-metric" key={label}>
                                <dt><span className="mdc-admin-icon"><i className={'pi ' + metricIcons[label]} aria-hidden="true" /></span>{label}</dt>
                                <dd>{count}</dd>
                            </div>
                        ))}
                    </dl>
                ) : <p className="mdc-admin-catalogue-message">{loading ? 'Checking catalogue…' : 'Catalogue counts are unavailable.'}</p>}
                <div className="mdc-admin-refresh">
                    <Button type="button" label="Refresh checks" icon="pi pi-refresh" outlined
                        className="mdc-admin-action mdc-admin-action--outline" loading={loading} disabled={loading} onClick={refresh} />
                </div>
            </Panel>
        </>
    );
};

export default AdminAuditPanel;
