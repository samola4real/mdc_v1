import React from 'react';
import { Card } from 'primereact/card';
import AdminAuditPanel from '@/components/mdc/AdminAuditPanel';
import DemoRoleGuard from '@/components/mdc/DemoRoleGuard';

const AdminAudit = () => {
    return (
        <div className="mdc-admin-dashboard">
            <Card className="mdc-admin-header">
                <h1>Admin Dashboard</h1>
                <p>Manage providers and check system availability.</p>
            </Card>
            <DemoRoleGuard allowedRoles={['admin']} pageLabel="Admin">
                <AdminAuditPanel />
            </DemoRoleGuard>
        </div>
    );
};

export default AdminAudit;
