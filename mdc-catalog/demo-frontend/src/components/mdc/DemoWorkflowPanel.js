import React from 'react';
import Link from 'next/link';
import { Button } from 'primereact/button';
import { Panel } from 'primereact/panel';
import { Divider } from 'primereact/divider';
import { workflowSteps } from './mockData';

const DemoWorkflowPanel = () => {
    return (
        <Panel header="MDC demo workflow" className="mt-4">
            <div className="grid">
                {workflowSteps.map((step, index) => (
                    <div className="col-12 md:col-6 lg:col-4" key={step}>
                        <div className="surface-card border-1 surface-border border-round p-3 h-full">
                            <div className="flex align-items-center gap-3">
                                <span className="inline-flex align-items-center justify-content-center border-circle bg-primary text-primary-contrast font-bold" style={{ width: '2rem', height: '2rem' }}>
                                    {index + 1}
                                </span>
                                <span className="font-medium text-900">{step}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            <Divider />
            <div className="flex flex-wrap gap-2">
                <Link href="/demo/provider">
                    <Button label="Provider Demo" icon="pi pi-building" />
                </Link>
                <Link href="/demo/consumer-search">
                    <Button label="Consumer Search" icon="pi pi-search" outlined />
                </Link>
                <Link href="/demo/admin-audit">
                    <Button label="Admin / Audit" icon="pi pi-shield" outlined />
                </Link>
            </div>
        </Panel>
    );
};

export default DemoWorkflowPanel;
