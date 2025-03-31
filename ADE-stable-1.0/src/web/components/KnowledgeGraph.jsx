import React, { useEffect, useRef } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import * as d3 from 'd3';
import { ForceGraph2D } from 'react-force-graph';

const KnowledgeGraph = ({ entries, relationships }) => {
  const graphRef = useRef(null);

  // Transform data for visualization
  const graphData = {
    nodes: entries.map(entry => ({
      id: entry.id,
      name: entry.topic,
      val: entry.importance_score * 10,
      color: entry.importance_score > 0.7 ? '#4caf50' : 
             entry.importance_score > 0.4 ? '#ff9800' : '#f44336'
    })),
    links: relationships.map(rel => ({
      source: rel.source_id,
      target: rel.target_id,
      value: rel.strength,
      type: rel.type
    }))
  };

  useEffect(() => {
    if (graphRef.current) {
      const graph = ForceGraph2D()(graphRef.current)
        .graphData(graphData)
        .nodeLabel('name')
        .nodeAutoColorBy('group')
        .linkDirectionalParticles(1)
        .linkDirectionalParticleSpeed(0.004)
        .d3Force('charge').strength(-100)
        .d3Force('link').distance(100)
        .d3Force('center').strength(0.5);

      return () => {
        graph._destructor();
      };
    }
  }, [entries, relationships]);

  return (
    <Paper sx={{ p: 2, height: '600px' }}>
      <Typography variant="h6" gutterBottom>
        Knowledge Network
      </Typography>
      <Box ref={graphRef} sx={{ height: 'calc(100% - 40px)' }} />
    </Paper>
  );
};

export default KnowledgeGraph; 