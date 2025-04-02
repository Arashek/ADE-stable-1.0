import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Typography, useTheme, alpha, Paper } from '@mui/material';
import { Agent, AgentStatus, AgentType } from './AgentListPanel';

// Define the node data structure for the graph
interface NodeData {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  x: number;
  y: number;
  size: number;
}

// Define the link data structure for the graph
interface LinkData {
  source: string;
  target: string;
  value: number;
  type: string;
}

// Props for the AgentNetworkVisualization component
interface AgentNetworkVisualizationProps {
  agents: Agent[];
  selectedAgentId?: string;
  onNodeClick?: (nodeId: string) => void;
}

/**
 * Simple Agent Network Visualization Component
 * This is a placeholder implementation that displays agents as circles in a static layout
 * It will be replaced with a more sophisticated force-directed graph visualization once dependencies are resolved
 */
const AgentNetworkVisualization: React.FC<AgentNetworkVisualizationProps> = ({
  agents,
  selectedAgentId,
  onNodeClick
}) => {
  const theme = useTheme();
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [links, setLinks] = useState<LinkData[]>([]);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // Position nodes in a circular layout
  const generateCircularLayout = useCallback(() => {
    if (!containerRef.current) return;
    
    const { width, height } = containerRef.current.getBoundingClientRect();
    setDimensions({ width, height });
    
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.4;
    
    const nodeList: NodeData[] = [];
    const linkList: LinkData[] = [];
    
    // Position nodes in a circle
    agents.forEach((agent, index) => {
      const angle = (2 * Math.PI * index) / agents.length;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      nodeList.push({
        id: agent.id,
        name: agent.name,
        type: agent.type,
        status: agent.status,
        x,
        y,
        size: agent.status === AgentStatus.ACTIVE || agent.status === AgentStatus.PROCESSING ? 25 : 20
      });
    });
    
    // Create some connections between nodes
    for (let i = 0; i < agents.length; i++) {
      const source = agents[i].id;
      
      // Connect to 1-3 random other nodes
      const numConnections = Math.floor(Math.random() * 3) + 1;
      const connectedIndices = new Set<number>();
      
      for (let j = 0; j < numConnections; j++) {
        let targetIndex;
        do {
          targetIndex = Math.floor(Math.random() * agents.length);
        } while (targetIndex === i || connectedIndices.has(targetIndex));
        
        connectedIndices.add(targetIndex);
        const target = agents[targetIndex].id;
        
        const relationshipTypes = ['depends', 'communicates', 'collaborates', 'validates'];
        const randomType = relationshipTypes[Math.floor(Math.random() * relationshipTypes.length)];
        
        linkList.push({
          source,
          target,
          value: Math.random() * 5 + 1,
          type: randomType
        });
      }
    }
    
    setNodes(nodeList);
    setLinks(linkList);
    setLoading(false);
  }, [agents]);

  // Initialize layout
  useEffect(() => {
    const timeout = setTimeout(() => {
      generateCircularLayout();
    }, 500);
    
    return () => clearTimeout(timeout);
  }, [generateCircularLayout]);

  // Update dimensions on resize
  useEffect(() => {
    if (!containerRef.current) return;
    
    const handleResize = () => {
      generateCircularLayout();
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [generateCircularLayout]);
  
  // Get node color based on agent type
  const getNodeColor = useCallback((type: AgentType) => {
    switch (type) {
      case AgentType.VALIDATOR:
        return '#7E57C2'; // Purple
      case AgentType.DESIGNER:
        return '#42A5F5'; // Blue
      case AgentType.ARCHITECT:
        return '#66BB6A'; // Green
      case AgentType.SECURITY:
        return '#EF5350'; // Red
      case AgentType.PERFORMANCE:
        return '#FFA726'; // Orange
      case AgentType.ADMIN:
        return '#78909C'; // Blue Grey
      default:
        return theme.palette.grey[500];
    }
  }, [theme]);
  
  // Get status color based on agent status
  const getStatusColor = useCallback((status: AgentStatus) => {
    switch (status) {
      case AgentStatus.ACTIVE:
        return theme.palette.success.main;
      case AgentStatus.IDLE:
        return theme.palette.grey[500];
      case AgentStatus.WARNING:
        return theme.palette.warning.main;
      case AgentStatus.ERROR:
        return theme.palette.error.main;
      case AgentStatus.PROCESSING:
        return theme.palette.info.main;
      default:
        return theme.palette.grey[500];
    }
  }, [theme]);
  
  // Get link color based on relationship type
  const getLinkColor = useCallback((type: string) => {
    switch (type) {
      case 'depends':
        return alpha(theme.palette.primary.main, 0.6);
      case 'communicates':
        return alpha(theme.palette.info.main, 0.6);
      case 'collaborates':
        return alpha(theme.palette.success.main, 0.6);
      case 'validates':
        return alpha(theme.palette.warning.main, 0.6);
      default:
        return alpha(theme.palette.grey[500], 0.6);
    }
  }, [theme]);
  
  // Handle node click
  const handleNodeClick = (nodeId: string) => {
    if (onNodeClick) {
      onNodeClick(nodeId);
    }
  };

  if (loading) {
    return (
      <Box 
        sx={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <CircularProgress size={40} />
        <Typography variant="body2" color="textSecondary">
          Loading agent network...
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        height: '100%',
        width: '100%',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <svg width={dimensions.width} height={dimensions.height}>
        {/* Draw links */}
        {links.map((link, index) => {
          const sourceNode = nodes.find(n => n.id === link.source);
          const targetNode = nodes.find(n => n.id === link.target);
          
          if (!sourceNode || !targetNode) return null;
          
          return (
            <line
              key={`link-${index}`}
              x1={sourceNode.x}
              y1={sourceNode.y}
              x2={targetNode.x}
              y2={targetNode.y}
              stroke={getLinkColor(link.type)}
              strokeWidth={link.value / 2 + 1}
              strokeDasharray={link.type === 'depends' ? '5,5' : undefined}
            />
          );
        })}
        
        {/* Draw nodes */}
        {nodes.map((node) => {
          const isSelected = node.id === selectedAgentId;
          const nodeColor = getNodeColor(node.type);
          const statusColor = getStatusColor(node.status);
          const isPulsing = node.status === AgentStatus.PROCESSING;
          
          return (
            <g 
              key={node.id} 
              transform={`translate(${node.x},${node.y})`}
              onClick={() => handleNodeClick(node.id)}
              style={{ cursor: 'pointer' }}
            >
              {/* Pulsing effect for processing nodes */}
              {isPulsing && (
                <circle
                  r={node.size + 5}
                  fill="none"
                  stroke={statusColor}
                  strokeWidth={2}
                  opacity={0.5}
                  style={{
                    animation: 'pulse 2s infinite'
                  }}
                />
              )}
              
              {/* Status ring */}
              <circle
                r={node.size + 2}
                fill="none"
                stroke={statusColor}
                strokeWidth={2}
              />
              
              {/* Selection ring */}
              {isSelected && (
                <circle
                  r={node.size + 5}
                  fill="none"
                  stroke={theme.palette.primary.main}
                  strokeWidth={2}
                />
              )}
              
              {/* Main node circle */}
              <circle
                r={node.size}
                fill={nodeColor}
              />
              
              {/* Node label */}
              <text
                textAnchor="middle"
                dy="0.3em"
                fill={theme.palette.getContrastText(nodeColor)}
                fontSize="12px"
                fontWeight="bold"
              >
                {node.name.split(' ')[0]}
              </text>
            </g>
          );
        })}
      </svg>
      
      {/* Legend */}
      <Paper
        elevation={2}
        sx={{
          position: 'absolute',
          bottom: 10,
          right: 10,
          p: 1,
          borderRadius: 1,
          bgcolor: alpha(theme.palette.background.paper, 0.8)
        }}
      >
        <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 0.5 }}>
          Connection Types:
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 3, bgcolor: getLinkColor('depends'), borderRadius: 1 }} />
            <Typography variant="caption">Depends (dashed)</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 3, bgcolor: getLinkColor('communicates'), borderRadius: 1 }} />
            <Typography variant="caption">Communicates</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 3, bgcolor: getLinkColor('collaborates'), borderRadius: 1 }} />
            <Typography variant="caption">Collaborates</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 3, bgcolor: getLinkColor('validates'), borderRadius: 1 }} />
            <Typography variant="caption">Validates</Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default AgentNetworkVisualization;
