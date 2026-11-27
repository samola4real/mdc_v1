import React from 'react';
import ConsumerSearchMockup from '@/components/mdc/ConsumerSearchMockup';
import DemoRoleGuard from '@/components/mdc/DemoRoleGuard';

const ConsumerSearch = () => {
    return (
        <div className="mdc-consumer">
            <header className="mdc-consumer-header">
                <h1>Manufacturing Service Discovery</h1>
                <p>
                    Find manufacturing providers that meet your technical requirements. Specify your part type, materials, manufacturing processes and technical specifications to discover eligible manufacturing services.
                </p>
            </header>
            <DemoRoleGuard allowedRoles={['consumer', 'admin']} pageLabel="Consumer or Admin">
                <ConsumerSearchMockup />
            </DemoRoleGuard>
        </div>
    );
};

export default ConsumerSearch;
