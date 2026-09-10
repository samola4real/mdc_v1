import React, { useCallback, useMemo, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { Toast } from 'primereact/toast';
import { Button } from 'primereact/button';
import DesignerPalette from '@/components/DesignerPalette';
import DesignerInspector from '@/components/DesignerInspector';
import StatusStrip from '@/components/StatusStrip';

const DesignerCanvas = dynamic(() => import('@/components/DesignerCanvas'), {
    ssr: false,
    loading: () => <div className="designer-canvas designer-canvas--loading">Loading designer…</div>
});

const PALETTE_GROUPS = [
    {
        label: 'Physical',
        items: [
            { kind: 'asset',   label: 'Asset',   description: 'Machine, cell, AGV',  icon: 'pi pi-box',         tone: 'navy'   },
            { kind: 'sensor',  label: 'Sensor',  description: 'Temperature, etc',    icon: 'pi pi-chart-line',  tone: 'orange' }
        ]
    },
    {
        label: 'Logical',
        items: [
            { kind: 'process', label: 'Process', description: 'Operation, step',     icon: 'pi pi-cog',        tone: 'sand' },
            { kind: 'storage', label: 'Storage', description: 'Edge data buffer',    icon: 'pi pi-database',   tone: 'ok'   }
        ]
    }
];

const NODE_DEFAULTS = {
    asset:   { label: 'New Asset',   assetType: 'Machine',     capacity: 100 },
    sensor:  { label: 'New Sensor',  metric: 'Temperature',    sampleHz: 10  },
    process: { label: 'New Process', duration: 30,             priority: 'Medium' },
    storage: { label: 'Edge Store',  capacityGb: 128,          retention: '30d' }
};

const INITIAL_NODES = [
    { id: 'n1', position: { x: 60,  y: 80  }, data: { label: 'Press #4',     __kind: 'asset',   assetType: 'Machine',     capacity: 150 },     className: 'rf-node rf-node--asset'   },
    { id: 'n2', position: { x: 320, y: 60  }, data: { label: 'Vibration',    __kind: 'sensor',  metric: 'Vibration',      sampleHz: 200 },     className: 'rf-node rf-node--sensor'  },
    { id: 'n3', position: { x: 320, y: 180 }, data: { label: 'Temperature',  __kind: 'sensor',  metric: 'Temperature',    sampleHz: 10  },     className: 'rf-node rf-node--sensor'  },
    { id: 'n4', position: { x: 600, y: 120 }, data: { label: 'OEE pipeline', __kind: 'process', duration: 5,              priority: 'High' },  className: 'rf-node rf-node--process' },
    { id: 'n5', position: { x: 860, y: 120 }, data: { label: 'EDGE Store',   __kind: 'storage', capacityGb: 256,          retention: '90d' },  className: 'rf-node rf-node--storage' }
];

const INITIAL_EDGES = [
    { id: 'e1', source: 'n1', target: 'n2', animated: true },
    { id: 'e2', source: 'n1', target: 'n3', animated: true },
    { id: 'e3', source: 'n2', target: 'n4' },
    { id: 'e4', source: 'n3', target: 'n4' },
    { id: 'e5', source: 'n4', target: 'n5' }
];

/* ------------------------------------------------------------ */

const Designer = () => {
    const toast = useRef(null);
    const [nodes, setNodes] = useState(INITIAL_NODES);
    const [edges, setEdges] = useState(INITIAL_EDGES);
    const [selectedId, setSelectedId] = useState(null);

    const selectedNode = useMemo(() => {
        const found = nodes.find((n) => n.id === selectedId);
        if (!found) return null;
        return { id: found.id, type: found.data?.__kind || 'asset', data: found.data };
    }, [nodes, selectedId]);

    /**
     * Add a node either from a palette drag-drop (position from caller) or
     * from a click on the palette (no position → centred default).
     */
    const addNode = useCallback((kind, position = { x: 200, y: 200 }) => {
        const id = `n${Date.now()}`;
        const defaults = NODE_DEFAULTS[kind] || NODE_DEFAULTS.asset;
        setNodes((curr) => [...curr, {
            id,
            position,
            data: { ...defaults, __kind: kind },
            className: `rf-node rf-node--${kind}`
        }]);
        toast.current?.show({ severity: 'success', summary: 'Node added', detail: `${defaults.label} (${kind})`, life: 1500 });
    }, []);

    const updateNodeData = useCallback((id, nextData) => {
        setNodes((curr) => curr.map((n) => (n.id === id ? { ...n, data: { ...n.data, ...nextData } } : n)));
    }, []);

    const deleteNode = useCallback((id) => {
        setNodes((curr) => curr.filter((n) => n.id !== id));
        setEdges((curr) => curr.filter((e) => e.source !== id && e.target !== id));
        setSelectedId(null);
        toast.current?.show({ severity: 'warn', summary: 'Deleted', detail: `Node ${id} removed.`, life: 1500 });
    }, []);

    const saveDiagram = () => {
        const payload = JSON.stringify({ nodes, edges }, null, 2);
        navigator.clipboard?.writeText(payload).catch(() => {});
        toast.current?.show({
            severity: 'success',
            summary: 'Diagram serialised',
            detail: 'Pasted to clipboard. Replace with POST /diagrams in production.',
            life: 2400
        });
    };

    const resetDiagram = () => {
        setNodes(INITIAL_NODES);
        setEdges(INITIAL_EDGES);
        setSelectedId(null);
    };

    return (
        <div className="designer-page">
            <Toast ref={toast} position="top-right" />

            <StatusStrip
                connection={{ label: 'Designer', value: 'Local draft', tone: 'warn' }}
                pills={[
                    { label: 'Nodes', value: nodes.length, tone: 'info' },
                    { label: 'Edges', value: edges.length, tone: 'muted' }
                ]}
            />

            <header className="designer-header">
                <div>
                    <span className="designer-header__tag">Workspace · Designer</span>
                    <h1>Data Flow designer</h1>
                    <p>
                        Drag components from the left rail onto the canvas, connect ports by
                        dragging from one handle to another, edit properties on the right.
                    </p>
                </div>
                <div className="designer-header__actions">
                    <Button label="Save" icon="pi pi-save" onClick={saveDiagram} />
                    <Button label="Reset" icon="pi pi-refresh" outlined onClick={resetDiagram} />
                </div>
            </header>

            <section className="designer-shell">
                <DesignerPalette groups={PALETTE_GROUPS} onAddNode={(kind) => addNode(kind)} />

                <div className="designer-canvas">
                    <DesignerCanvas
                        nodes={nodes}
                        edges={edges}
                        setNodes={setNodes}
                        setEdges={setEdges}
                        selectedId={selectedId}
                        setSelectedId={setSelectedId}
                        onAddNode={addNode}
                    />
                </div>

                <DesignerInspector
                    node={selectedNode}
                    onChange={updateNodeData}
                    onDelete={deleteNode}
                />
            </section>
        </div>
    );
};

export default Designer;
