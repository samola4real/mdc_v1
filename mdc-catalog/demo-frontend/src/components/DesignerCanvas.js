import React, { useCallback, useRef } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    ReactFlowProvider,
    useReactFlow,
    applyNodeChanges,
    applyEdgeChanges,
    addEdge
} from 'reactflow';

/* ============================================================================
   DesignerCanvas — encapsulates everything that depends on `reactflow`.
   The parent page loads this component via `next/dynamic` with ssr:false so
   reactflow lives in its own chunk and never runs on the server.
   ============================================================================ */

const minimapColor = (n) => {
    switch (n.data?.__kind) {
        case 'sensor':  return '#E78C3A';
        case 'process': return '#D8D1BE';
        case 'storage': return '#2BA86F';
        default:        return '#223F61';
    }
};

const InnerCanvas = ({ nodes, edges, setNodes, setEdges, selectedId, setSelectedId, onAddNode }) => {
    const wrapperRef = useRef(null);
    const { screenToFlowPosition } = useReactFlow();

    const onNodesChange = useCallback((changes) => {
        setNodes((curr) => applyNodeChanges(changes, curr));
        for (const c of changes) {
            if (c.type === 'select') {
                if (c.selected) setSelectedId(c.id);
                else if (selectedId === c.id) setSelectedId(null);
            }
            if (c.type === 'remove' && selectedId === c.id) {
                setSelectedId(null);
            }
        }
    }, [setNodes, selectedId, setSelectedId]);

    const onEdgesChange = useCallback((changes) => {
        setEdges((curr) => applyEdgeChanges(changes, curr));
    }, [setEdges]);

    const onConnect = useCallback((connection) => {
        setEdges((curr) => addEdge({ ...connection, animated: true }, curr));
    }, [setEdges]);

    const onDragOver = useCallback((event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback((event) => {
        event.preventDefault();
        const kind = event.dataTransfer.getData('application/maasai-node');
        if (!kind || !wrapperRef.current) return;

        // screenToFlowPosition transparently handles pan/zoom.
        const position = screenToFlowPosition({
            x: event.clientX,
            y: event.clientY
        });

        onAddNode(kind, position);
    }, [screenToFlowPosition, onAddNode]);

    return (
        <div className="designer-canvas-inner" ref={wrapperRef} onDragOver={onDragOver} onDrop={onDrop}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
                fitViewOptions={{ padding: 0.2 }}
                deleteKeyCode={['Delete', 'Backspace']}
                proOptions={{ hideAttribution: true }}
            >
                <Background gap={20} size={1} color="#D8D1BE" />
                <Controls position="bottom-right" showInteractive={false} />
                <MiniMap pannable zoomable maskColor="rgba(34, 63, 97, 0.08)" nodeColor={minimapColor} />
            </ReactFlow>
        </div>
    );
};

/* The provider wrapper is required so children (and the dropzone) can use
   `useReactFlow()` for coordinate conversion. */
const DesignerCanvas = (props) => (
    <ReactFlowProvider>
        <InnerCanvas {...props} />
    </ReactFlowProvider>
);

export default DesignerCanvas;
