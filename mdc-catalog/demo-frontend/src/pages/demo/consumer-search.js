import React from 'react';
import ConsumerSearchMockup from '@/components/mdc/ConsumerSearchMockup';
import DemoRoleGuard from '@/components/mdc/DemoRoleGuard';
import { useSelectedDemoRole } from '@/components/mdc/demoAuth';
import { useAuth } from '@/layout/context/AuthContext';

const ConsumerSearch = () => {
    const { authenticated, keycloak } = useAuth();
    const role = useSelectedDemoRole();
    const searchScope = JSON.stringify([authenticated, role, keycloak?.subject, keycloak?.sessionId]);
    return (
        <div className="mdc-consumer">
            <header className="mdc-consumer-header">
                <h1>Manufacturing Service Discovery</h1>
                <p>
                    Find manufacturing providers that meet your technical requirements. Specify your part type, materials, manufacturing processes and technical specifications to discover eligible manufacturing services.
                </p>
            </header>
            <DemoRoleGuard allowedRoles={['consumer', 'admin']} pageLabel="Consumer or Admin">
                <ConsumerSearchMockup key={searchScope} />
            </DemoRoleGuard>
        </div>
    );
};

export default ConsumerSearch;
