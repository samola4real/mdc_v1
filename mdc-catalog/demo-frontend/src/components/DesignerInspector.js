import React from 'react';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';

/**
 * Right-rail inspector. Renders editable properties for the selected node.
 *
 * Each node carries a `data` object whose fields we render; the inspector
 * is schema-driven via `NODE_SCHEMAS` keyed by node kind. Add new kinds by
 * declaring a schema entry — no extra wiring needed.
 */
export const NODE_SCHEMAS = {
    asset: [
        { name: 'label',       label: 'Name',          kind: 'text' },
        { name: 'assetType',   label: 'Asset type',    kind: 'dropdown', options: ['Machine', 'AGV', 'Operator', 'Cell'] },
        { name: 'capacity',    label: 'Capacity',      kind: 'number',   min: 0 }
    ],
    sensor: [
        { name: 'label',       label: 'Name',          kind: 'text' },
        { name: 'metric',      label: 'Metric',        kind: 'dropdown', options: ['Temperature', 'Vibration', 'Current', 'Pressure'] },
        { name: 'sampleHz',    label: 'Sample rate (Hz)', kind: 'number', min: 1 }
    ],
    process: [
        { name: 'label',       label: 'Name',          kind: 'text' },
        { name: 'duration',    label: 'Duration (min)', kind: 'number', min: 0 },
        { name: 'priority',    label: 'Priority',      kind: 'dropdown', options: ['Low', 'Medium', 'High', 'Critical'] }
    ],
    storage: [
        { name: 'label',       label: 'Name',          kind: 'text' },
        { name: 'capacityGb',  label: 'Capacity (GB)', kind: 'number', min: 1 },
        { name: 'retention',   label: 'Retention',     kind: 'dropdown', options: ['7d', '30d', '90d', '1y', '5y'] }
    ]
};

const DesignerInspector = ({ node, onChange, onDelete }) => {
    if (!node) {
        return (
            <aside className="designer-inspector designer-inspector--empty">
                <p>Select a node on the canvas to edit its properties.</p>
            </aside>
        );
    }

    const schema = NODE_SCHEMAS[node.type] || NODE_SCHEMAS.asset;
    const setField = (name, value) => onChange?.(node.id, { ...node.data, [name]: value });

    return (
        <aside className="designer-inspector">
            <header>
                <span className="designer-inspector__kind">{node.type}</span>
                <strong>{node.data?.label || node.id}</strong>
            </header>

            <div className="designer-inspector__fields">
                {schema.map((field) => {
                    if (field.kind === 'text') {
                        return (
                            <label key={field.name}>
                                <span>{field.label}</span>
                                <InputText
                                    value={node.data?.[field.name] || ''}
                                    onChange={(e) => setField(field.name, e.target.value)}
                                />
                            </label>
                        );
                    }
                    if (field.kind === 'number') {
                        return (
                            <label key={field.name}>
                                <span>{field.label}</span>
                                <InputNumber
                                    value={node.data?.[field.name]}
                                    onValueChange={(e) => setField(field.name, e.value)}
                                    min={field.min}
                                    max={field.max}
                                />
                            </label>
                        );
                    }
                    if (field.kind === 'dropdown') {
                        return (
                            <label key={field.name}>
                                <span>{field.label}</span>
                                <Dropdown
                                    value={node.data?.[field.name]}
                                    options={field.options}
                                    onChange={(e) => setField(field.name, e.value)}
                                />
                            </label>
                        );
                    }
                    return null;
                })}
            </div>

            <footer>
                <Button label="Delete node" icon="pi pi-trash" severity="danger" outlined onClick={() => onDelete?.(node.id)} />
            </footer>
        </aside>
    );
};

export default DesignerInspector;
