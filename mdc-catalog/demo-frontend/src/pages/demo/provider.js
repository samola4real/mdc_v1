import React from 'react';
import { Card } from 'primereact/card';
import DemoRoleGuard from '@/components/mdc/DemoRoleGuard';
import ProviderDemoPanel from '@/components/mdc/ProviderDemoPanel';

const ProviderDemo = () => {
    return (
        <div className="flex flex-column gap-4">
            <Card>
                <div className="text-sm text-600 mb-2">MDC Demo Console</div>
                <h1 className="mt-0 mb-0 text-900">Provider Dashboard</h1>
                <p className="text-600 line-height-3 mb-0 mt-2">
                    Demo persistence illustrates a future Marketplace-mediated provider lifecycle.
                    These controls are not the production trusted lifecycle and may be unavailable
                    when the backend demo API is disabled.
                </p>
            </Card>
            <DemoRoleGuard allowedRoles={['provider', 'admin']} pageLabel="Provider or Admin">
                <ProviderDemoPanel />
            </DemoRoleGuard>
        </div>
    );
};

export default ProviderDemo;
