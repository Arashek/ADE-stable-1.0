import React, { useEffect, useRef } from 'react';
import ForceGraph3D from '3d-force-graph';
import { Box, Paper, Typography, IconButton, Tooltip } from '@mui/material';
import { Refresh as RefreshIcon, ZoomIn, ZoomOut, CenterFocusStrong } from '@mui/icons-material';
import { DependencyService } from '../../services/dependency/DependencyService';

interface Node {
  id: string;
  name: string;
  val: number;
  color: string;
  group: string;
}

interface Link {
  source: string;
  target: string;
  value: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

export const CodeDependencyGraph: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const initGraph = async () => {
      const dependencyService = DependencyService.getInstance();
      const dependencies = await dependencyService.analyzeDependencies();
      
      const graphData = transformDependenciesToGraphData(dependencies);
      
      graphRef.current = ForceGraph3D()(containerRef.current)
        .graphData(graphData)
        .nodeLabel('name')
        .nodeColor(node => (node as Node).color)
        .nodeVal(node => (node as Node).val)
        .linkWidth(link => (link as Link).value)
        .linkDirectionalParticles(2)
        .linkDirectionalParticleWidth(2)
        .onNodeClick(handleNodeClick)
        .onBackgroundClick(handleBackgroundClick);

      // Add camera controls
      graphRef.current
        .controls()
        .enableDamping = true;
    };

    initGraph();

    return () => {
      if (graphRef.current) {
        graphRef.current._destructor();
      }
    };
  }, []);

  const transformDependenciesToGraphData = (dependencies: any): GraphData => {
    const nodes: Node[] = [];
    const links: Link[] = [];
    const colors = {
      component: '#ff7676',
      service: '#4CAF50',
      util: '#2196F3',
      model: '#9C27B0',
      test: '#795548',
    };

    // Transform dependencies into graph data
    dependencies.modules.forEach((module: any) => {
      nodes.push({
        id: module.path,
        name: module.name,
        val: module.complexity || 1,
        color: colors[module.type as keyof typeof colors] || '#999',
        group: module.type,
      });

      module.dependencies.forEach((dep: string) => {
        links.push({
          source: module.path,
          target: dep,
          value: 1,
        });
      });
    });

    return { nodes, links };
  };

  const handleNodeClick = (node: Node) => {
    const distance = 40;
    const distRatio = 1 + distance/Math.hypot(node.x!, node.y!, node.z!);

    if (graphRef.current) {
      graphRef.current.cameraPosition(
        { x: node.x! * distRatio, y: node.y! * distRatio, z: node.z! * distRatio },
        node,
        1000
      );
    }
  };

  const handleBackgroundClick = () => {
    if (graphRef.current) {
      graphRef.current.cameraPosition(
        { x: 0, y: 0, z: 200 },
        { x: 0, y: 0, z: 0 },
        1000
      );
    }
  };

  const handleRefresh = async () => {
    const dependencyService = DependencyService.getInstance();
    const dependencies = await dependencyService.analyzeDependencies();
    const graphData = transformDependenciesToGraphData(dependencies);
    
    if (graphRef.current) {
      graphRef.current.graphData(graphData);
    }
  };

  const handleZoomIn = () => {
    if (graphRef.current) {
      const currentDistance = graphRef.current.camera().position.z;
      graphRef.current.cameraPosition(
        { z: currentDistance * 0.7 },
        undefined,
        500
      );
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      const currentDistance = graphRef.current.camera().position.z;
      graphRef.current.cameraPosition(
        { z: currentDistance * 1.3 },
        undefined,
        500
      );
    }
  };

  const handleCenter = () => {
    handleBackgroundClick();
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Code Dependency Visualization</Typography>
        <Box>
          <Tooltip title="Zoom In">
            <IconButton onClick={handleZoomIn} size="small">
              <ZoomIn />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton onClick={handleZoomOut} size="small">
              <ZoomOut />
            </IconButton>
          </Tooltip>
          <Tooltip title="Center View">
            <IconButton onClick={handleCenter} size="small">
              <CenterFocusStrong />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      <Box ref={containerRef} sx={{ flex: 1 }} />
    </Paper>
  );
}; 