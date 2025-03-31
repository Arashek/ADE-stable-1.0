import React, { useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon
} from '@mui/icons-material';
import { useAgentContext } from '../../contexts/AgentContext';
import * as d3 from 'd3';

interface AgentVisualizationProps {
  projectId: string;
}

interface Node {
  id: string;
  name: string;
  type: 'file' | 'directory' | 'agent';
  children?: Node[];
  agentFocus?: number;
}

const AgentVisualization: React.FC<AgentVisualizationProps> = ({ projectId }) => {
  const { state } = useAgentContext();
  const svgRef = useRef<SVGSVGElement>(null);
  const [activeTab, setActiveTab] = React.useState(0);
  const [isLoading, setIsLoading] = React.useState(true);
  const [zoom, setZoom] = React.useState(1);

  // Mock data - replace with actual data from backend
  const mockData: Node = {
    id: 'root',
    name: 'Project Root',
    type: 'directory',
    children: [
      {
        id: 'src',
        name: 'src',
        type: 'directory',
        agentFocus: 0.8,
        children: [
          {
            id: 'components',
            name: 'components',
            type: 'directory',
            agentFocus: 0.6,
            children: [
              { id: 'App.tsx', name: 'App.tsx', type: 'file', agentFocus: 0.9 },
              { id: 'index.tsx', name: 'index.tsx', type: 'file', agentFocus: 0.7 }
            ]
          }
        ]
      }
    ]
  };

  useEffect(() => {
    if (svgRef.current) {
      renderVisualization();
    }
  }, [activeTab, zoom]);

  const renderVisualization = () => {
    if (!svgRef.current) return;

    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Clear previous visualization
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select<SVGSVGElement, unknown>(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create zoom behavior
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        setZoom(event.transform.k);
      });

    svg.call(zoomBehavior);

    // Create the visualization based on active tab
    switch (activeTab) {
      case 0:
        renderProjectStructure(svg, width, height, margin);
        break;
      case 1:
        renderAgentFocus(svg, width, height, margin);
        break;
      case 2:
        renderDependencies(svg, width, height, margin);
        break;
      default:
        break;
    }
  };

  const renderProjectStructure = (
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    width: number,
    height: number,
    margin: { top: number; right: number; bottom: number; left: number }
  ) => {
    const treeLayout = d3.tree<Node>()
      .size([height - margin.top - margin.bottom, width - margin.left - margin.right]);

    const root = d3.hierarchy(mockData);
    const treeData = treeLayout(root);

    // Add links
    svg.selectAll('path.link')
      .data(treeData.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d => {
        const link = d3.linkHorizontal()
          .x((d: any) => d.y)
          .y((d: any) => d.x);
        return link(d as any);
      })
      .attr('fill', 'none')
      .attr('stroke', '#ccc')
      .attr('stroke-width', 1.5);

    // Add nodes
    const nodes = svg.selectAll('g.node')
      .data(treeData.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y},${d.x})`);

    // Add circles for nodes
    nodes.append('circle')
      .attr('r', 6)
      .attr('fill', d => d.data.type === 'file' ? '#4CAF50' : '#2196F3')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels
    nodes.append('text')
      .attr('dy', '.35em')
      .attr('x', d => d.children ? -8 : 8)
      .attr('text-anchor', d => d.children ? 'end' : 'start')
      .text(d => d.data.name)
      .attr('font-size', '12px');
  };

  const renderAgentFocus = (
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    width: number,
    height: number,
    margin: { top: number; right: number; bottom: number; left: number }
  ) => {
    // Implementation for agent focus visualization
    // This would show heat maps or other visualizations of where agents are working
  };

  const renderDependencies = (
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    width: number,
    height: number,
    margin: { top: number; right: number; bottom: number; left: number }
  ) => {
    // Implementation for dependency visualization
    // This would show relationships between files and components
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.2, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.2, 0.5));
  };

  useEffect(() => {
    // Simulate loading data
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Project Visualization</Typography>
        <Box>
          <Tooltip title="Zoom In">
            <IconButton onClick={handleZoomIn} size="small">
              <ZoomInIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton onClick={handleZoomOut} size="small">
              <ZoomOutIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={() => setIsLoading(true)} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
      >
        <Tab label="Project Structure" />
        <Tab label="Agent Focus" />
        <Tab label="Dependencies" />
      </Tabs>

      <Paper sx={{ p: 2, overflow: 'auto' }}>
        <svg ref={svgRef}></svg>
      </Paper>
    </Box>
  );
};

export default AgentVisualization; 