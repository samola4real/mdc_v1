import React from 'react';
import { Card } from 'primereact/card';
import AdminAuditPanel from '@/components/mdc/AdminAuditPanel';
import DemoRoleGuard from '@/components/mdc/DemoRoleGuard';

const AdminAudit = () => {
    return (
        <div className="flex flex-column gap-4">
            <Card>
                <div className="text-sm text-600 mb-2">MDC Demo Console</div>
                <h1 className="mt-0 mb-2 text-900">Demo Admin Console</h1>
                <p className="text-600 line-height-3 mb-0">
                    Monitor the MDC demo status, registered demo provider state, and technical
                    service-discovery checks.
                </p>
            </Card>
            <DemoRoleGuard allowedRoles={['admin']} pageLabel="Admin">
                <AdminAuditPanel />
            </DemoRoleGuard>
        </div>
    );
};

export default AdminAudit;
