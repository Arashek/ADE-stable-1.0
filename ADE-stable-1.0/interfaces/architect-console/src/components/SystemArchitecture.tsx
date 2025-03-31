import React, { useCallback } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

// Initial nodes for demonstration
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Frontend' },
    position: { x: 250, y: 25 },
  },
  {
    id: '2',
    data: { label: 'API Gateway' },
    position: { x: 250, y: 125 },
  },
  {
    id: '3',
    data: { label: 'Authentication' },
    position: { x: 100, y: 225 },
  },
  {
    id: '4',
    data: { label: 'Database' },
    position: { x: 400, y: 225 },
  },
];

// Initial edges for demonstration
const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
  { id: 'e2-4', source: '2', target: '4' },
];

const SystemArchitecture: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => [...eds, params]),
    [setEdges]
  );

  return (
    <Paper
      elevation={3}
      sx={{
        height: '400px',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Typography variant="h6" gutterBottom>
        System Architecture
      </Typography>
      <Box sx={{ flex: 1, minHeight: 0 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </Box>
    </Paper>
  );
};

export default SystemArchitecture; 