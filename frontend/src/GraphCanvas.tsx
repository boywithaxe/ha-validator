import { useCallback, useEffect, useState } from 'react';
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    type Connection,
    type Edge,
    type Node
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import axios from 'axios';

interface GraphData {
    nodes: Node[];
    edges: Edge[];
}

export default function GraphCanvas() {
    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    // Full dataset retention for filtering
    const [allNodes, setAllNodes] = useState<Node[]>([]);
    const [allEdges, setAllEdges] = useState<Edge[]>([]);

    const [selectedAutomationId, setSelectedAutomationId] = useState<string>('');
    const [automations, setAutomations] = useState<{ id: string, label: string }[]>([]);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges],
    );

    useEffect(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        axios.get<GraphData>(`${apiUrl}/api/graph`)
            .then(res => {
                const rawNodes = res.data.nodes;
                const rawEdges = res.data.edges;
                setAllNodes(rawNodes);
                setAllEdges(rawEdges);

                // Extract Automations for dropdown
                const autos = rawNodes
                    .filter(n => n.data.type === 'automation' || n.id.startsWith('automation.'))
                    .map(n => ({ id: n.id, label: (n.data.label as string) || n.id }));

                setAutomations(autos);

                // Default select first one if available to reduce noise
                if (autos.length > 0) {
                    setSelectedAutomationId(autos[0].id);
                } else {
                    setNodes(rawNodes); // If no automations, show all (fallback)
                    setEdges(rawEdges);
                }
            })
            .catch(err => console.error("Failed to fetch graph:", err));
    }, [setNodes, setEdges]);

    // Filtering Effect
    useEffect(() => {
        if (!selectedAutomationId || allNodes.length === 0) return;

        // Find the selected automation node
        const autoNode = allNodes.find(n => n.id === selectedAutomationId);
        if (!autoNode) return;

        // Find connected edges
        const relevantEdges = allEdges.filter(e => e.source === selectedAutomationId || e.target === selectedAutomationId);

        // Find connected entity nodes
        const neighborIds = new Set(relevantEdges.flatMap(e => [e.source, e.target]));
        neighborIds.add(selectedAutomationId); // Ensure central node is included

        const filteredNodes = allNodes.filter(n => neighborIds.has(n.id));

        setNodes(filteredNodes);
        setEdges(relevantEdges);

    }, [selectedAutomationId, allNodes, allEdges, setNodes, setEdges]);

    return (
        <div className="flex flex-col space-y-4">
            <div className="flex items-center space-x-2">
                <label className="text-gray-700 font-medium">Filter Automation:</label>
                <select
                    className="border p-2 rounded bg-white"
                    value={selectedAutomationId}
                    onChange={(e) => setSelectedAutomationId(e.target.value)}
                >
                    {automations.map(a => (
                        <option key={a.id} value={a.id}>{a.label}</option>
                    ))}
                </select>
                <span className="text-sm text-gray-500">
                    (Showing {nodes.length} nodes)
                </span>
            </div>

            <div style={{ width: '1000px', height: '600px' }} className="border rounded shadow-lg bg-white">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                >
                    <Controls />
                    <MiniMap />
                    <Background gap={12} size={1} />
                </ReactFlow>
            </div>
        </div>
    );
}
