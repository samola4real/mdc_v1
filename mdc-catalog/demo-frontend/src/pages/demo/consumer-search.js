import React from 'react';
import { Card } from 'primereact/card';
import ConsumerSearchMockup from '@/components/mdc/ConsumerSearchMockup';
import DemoRoleGuard from '@/components/mdc/DemoRoleGuard';

const ConsumerSearch = () => {
    return (
        <div className="flex flex-column gap-4">
            <Card>
                <div className="text-sm text-600 mb-2">MDC Demo Console</div>
                <h1 className="mt-0 mb-2 text-900">Consumer Search</h1>
                <p className="text-600 line-height-3 mb-0">
                    Marketplace-style service discovery flow connected to the MDC search endpoint.
                    Results focus on evidence; scores remain available only in advanced/debug details.
                </p>
            </Card>
            <DemoRoleGuard allowedRoles={['consumer', 'admin']} pageLabel="Consumer or Admin">
                <ConsumerSearchMockup />
            </DemoRoleGuard>
        </div>
    );
};

export default ConsumerSearch;
