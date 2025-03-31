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

// Initial nodes for the decision tree
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Architecture Decision' },
    position: { x: 250, y: 25 },
  },
  {
    id: '2',
    data: { label: 'Consideration 1' },
    position: { x: 100, y: 125 },
  },
  {
    id: '3',
    data: { label: 'Consideration 2' },
    position: { x: 400, y: 125 },
  },
  {
    id: '4',
    data: { label: 'Decision Point 1' },
    position: { x: 50, y: 225 },
  },
  {
    id: '5',
    data: { label: 'Decision Point 2' },
    position: { x: 250, y: 225 },
  },
  {
    id: '6',
    data: { label: 'Decision Point 3' },
    position: { x: 450, y: 225 },
  },
];

// Initial edges for the decision tree
const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e1-3', source: '1', target: '3' },
  { id: 'e2-4', source: '2', target: '4' },
  { id: 'e2-5', source: '2', target: '5' },
  { id: 'e3-5', source: '3', target: '5' },
  { id: 'e3-6', source: '3', target: '6' },
];

const DecisionTree: React.FC = () => {
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
        Decision Tree
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

export default DecisionTree; 