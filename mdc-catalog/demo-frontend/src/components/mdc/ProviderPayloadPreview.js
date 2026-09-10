import React from 'react';
import { Panel } from 'primereact/panel';

const ProviderPayloadPreview = ({ payload }) => (
    <Panel header="Advanced / payload preview" toggleable collapsed>
        <pre className="m-0 white-space-pre-wrap">{JSON.stringify(payload, null, 2)}</pre>
    </Panel>
);

export default ProviderPayloadPreview;
