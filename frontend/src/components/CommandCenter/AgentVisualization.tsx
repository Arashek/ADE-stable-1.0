import React, { useEffect, useRef, useState } from 'react';
import { ForceGraph2D } from 'react-force-graph';
import { Box, Typography, Paper, Tooltip } from '@mui/material';
import { AgentConfig, AgentRegistration } from '../../../backend/src/services/agent/AgentRegistry';
import { LLMEndpoint } from '../../../backend/src/services/agent/LLMProviderService';

interface Node {
  id: string;
  name: string;
  type: 'agent' | 'llm' | 'capability';
  status?: 'active' | 'inactive' | 'error';
  color?: string;
}

interface Link {
  source: string;
  target: string;
  type: 'uses' | 'provides' | 'requires';
  value: number;
}

interface AgentVisualizationProps {
  agents: AgentConfig[];
  registrations: AgentRegistration[];
  llmEndpoints: LLMEndpoint[];
  onNodeClick?: (node: Node) => void;
}

const AgentVisualization: React.FC<AgentVisualizationProps> = ({
  agents,
  registrations,
  llmEndpoints,
  onNodeClick
}) => {
  const graphRef = useRef<any>();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [links, setLinks] = useState<Link[]>([]);

  useEffect(() => {
    const graphNodes: Node[] = [];
    const graphLinks: Link[] = [];

    // Add agent nodes
    agents.forEach(agent => {
      const registration = registrations.find(r => r.agentId === agent.id);
      graphNodes.push({
        id: agent.id,
        name: agent.name,
        type: 'agent',
        status: registration?.status || 'inactive',
        color: getNodeColor('agent', registration?.status)
      });

      // Add capability nodes and links
      agent.capabilities.forEach(cap => {
        const capabilityId = `${agent.id}-${cap.id}`;
        graphNodes.push({
          id: capabilityId,
          name: cap.name,
          type: 'capability',
          color: getNodeColor('capability')
        });

        graphLinks.push({
          source: agent.id,
          target: capabilityId,
          type: 'provides',
          value: 1
        });

        // Add LLM requirement links
        cap.requiredLLMs.forEach(llmId => {
          const endpoint = llmEndpoints.find(e => e.model === llmId);
          if (endpoint) {
            graphLinks.push({
              source: capabilityId,
              target: endpoint.id,
              type: 'requires',
              value: 1
            });
          }
        });
      });
    });

    // Add LLM nodes
    llmEndpoints.forEach(endpoint => {
      graphNodes.push({
        id: endpoint.id,
        name: `${endpoint.provider} - ${endpoint.model}`,
        type: 'llm',
        status: endpoint.isActive ? 'active' : 'inactive',
        color: getNodeColor('llm', endpoint.isActive ? 'active' : 'inactive')
      });
    });

    setNodes(graphNodes);
    setLinks(graphLinks);
  }, [agents, registrations, llmEndpoints]);

  const getNodeColor = (type: string, status?: string): string => {
    if (type === 'agent') {
      switch (status) {
        case 'active': return '#4CAF50';
        case 'inactive': return '#9E9E9E';
        case 'error': return '#F44336';
        default: return '#9E9E9E';
      }
    } else if (type === 'llm') {
      return status === 'active' ? '#2196F3' : '#90CAF9';
    } else {
      return '#FFA726';
    }
  };

  const handleNodeClick = (node: any) => {
    if (onNodeClick) {
      onNodeClick(node);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>
        Agent Ecosystem Visualization
      </Typography>
      <Box sx={{ flexGrow: 1, minHeight: '500px' }}>
        <ForceGraph2D
          ref={graphRef}
          graphData={{ nodes, links }}
          nodeLabel="name"
          nodeColor={node => (node as Node).color || '#9E9E9E'}
          linkColor={link => {
            switch ((link as Link).type) {
              case 'provides': return '#4CAF50';
              case 'requires': return '#F44336';
              default: return '#9E9E9E';
            }
          }}
          linkWidth={link => (link as Link).value}
          onNodeClick={handleNodeClick}
          nodeRelSize={8}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          cooldownTicks={100}
          d3VelocityDecay={0.1}
        />
      </Box>
      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
        <Typography variant="body2">
          Nodes: {nodes.length} | Links: {links.length}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Tooltip title="Active Agents">
            <Box sx={{ width: 12, height: 12, bgcolor: '#4CAF50', borderRadius: '50%' }} />
          </Tooltip>
          <Tooltip title="Inactive Agents">
            <Box sx={{ width: 12, height: 12, bgcolor: '#9E9E9E', borderRadius: '50%' }} />
          </Tooltip>
          <Tooltip title="Error State">
            <Box sx={{ width: 12, height: 12, bgcolor: '#F44336', borderRadius: '50%' }} />
          </Tooltip>
          <Tooltip title="LLM Endpoints">
            <Box sx={{ width: 12, height: 12, bgcolor: '#2196F3', borderRadius: '50%' }} />
          </Tooltip>
          <Tooltip title="Capabilities">
            <Box sx={{ width: 12, height: 12, bgcolor: '#FFA726', borderRadius: '50%' }} />
          </Tooltip>
        </Box>
      </Box>
    </Paper>
  );
};

export default AgentVisualization; 