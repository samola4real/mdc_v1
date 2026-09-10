import React from 'react';
import { Card } from 'primereact/card';
import StatusTag from './StatusTag';
import { demoBackends } from './mockData';

const DemoStatusCards = ({ cards = demoBackends }) => {
    return (
        <div className="grid">
            {cards.map((item) => (
                <div className="col-12 md:col-6 lg:col-4" key={item.label}>
                    <Card className="h-full">
                        <div className="flex justify-content-between align-items-start gap-3">
                            <div>
                                <div className="text-sm text-600 mb-2">{item.label}</div>
                                <div className="text-xl font-semibold text-900">{item.value}</div>
                            </div>
                            <StatusTag value={item.statusLabel || item.tone} status={item.status || item.tone} />
                        </div>
                        <p className="text-600 line-height-3 mb-0">{item.description}</p>
                    </Card>
                </div>
            ))}
        </div>
    );
};

export default DemoStatusCards;
