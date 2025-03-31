import React, { useCallback, useMemo, useRef, useState } from 'react';
import { ForceGraph2D } from 'react-force-graph';
import {
  Box,
  Paper,
  Typography,
  useTheme,
  IconButton,
  TextField,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  CenterFocusStrong as CenterIcon,
  Search as SearchIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { CodeMetrics, DependencyGraph, DependencyNode, DependencyLink } from '../../types/visualization.types';

interface CodeVisualizationProps {
  code: string;
  metrics: CodeMetrics;
  dependencies: DependencyGraph;
  onNodeSelect?: (node: DependencyNode) => void;
}

const CodeVisualization: React.FC<CodeVisualizationProps> = ({
  code,
  metrics,
  dependencies,
  onNodeSelect
}) => {
  const theme = useTheme();
  const graphRef = useRef<any>();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [hoveredNode, setHoveredNode] = useState<DependencyNode | null>(null);

  const getNodeColor = useCallback((node: DependencyNode) => {
    if (!node.metrics) {
      return theme.palette.grey[500];
    }

    // Color based on complexity and maintainability
    const score = (node.metrics.complexity || 0) * (node.metrics.maintainability || 0);
    if (score > 0.8) return theme.palette.success.main;
    if (score > 0.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  }, [theme]);

  const getLinkColor = useCallback((link: DependencyLink) => {
    switch (link.type) {
      case 'imports':
        return theme.palette.primary.main;
      case 'calls':
        return theme.palette.secondary.main;
      case 'extends':
        return theme.palette.success.main;
      case 'implements':
        return theme.palette.info.main;
      default:
        return theme.palette.grey[500];
    }
  }, [theme]);

  const filteredData = useMemo(() => {
    let nodes = dependencies.nodes;
    
    // Apply search filter
    if (searchTerm) {
      nodes = nodes.filter(node => 
        node.label.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply type filter
    if (selectedTypes.length > 0) {
      nodes = nodes.filter(node => selectedTypes.includes(node.type));
    }

    // Get filtered node IDs
    const nodeIds = new Set(nodes.map(node => node.id));

    // Filter links based on filtered nodes
    const links = dependencies.links.filter(link =>
      nodeIds.has(link.source as string) && nodeIds.has(link.target as string)
    );

    return { nodes, links };
  }, [dependencies, searchTerm, selectedTypes]);

  const handleZoomIn = () => {
    if (graphRef.current) {
      const { current: graph } = graphRef;
      graph.zoom(graph.zoom() * 1.5);
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      const { current: graph } = graphRef;
      graph.zoom(graph.zoom() / 1.5);
    }
  };

  const handleCenter = () => {
    if (graphRef.current) {
      graphRef.current.centerAt(0, 0, 1000);
      graphRef.current.zoom(1, 1000);
    }
  };

  const handleNodeClick = useCallback((node: DependencyNode) => {
    if (onNodeSelect) {
      onNodeSelect(node);
    }
  }, [onNodeSelect]);

  const handleNodeHover = useCallback((node: DependencyNode | null) => {
    setHoveredNode(node);
  }, []);

  const availableTypes = useMemo(() => 
    Array.from(new Set(dependencies.nodes.map(node => node.type))),
    [dependencies.nodes]
  );

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: { xs: 'column', md: 'row' },
        gap: 2,
        p: 2,
        height: '100%',
        bgcolor: theme.palette.background.default
      }}
    >
      <Paper
        elevation={2}
        sx={{
          flex: 2,
          overflow: 'hidden',
          borderRadius: 2,
          bgcolor: theme.palette.background.paper,
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              size="small"
              placeholder="Search nodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />
              }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Filter by type</InputLabel>
              <Select
                multiple
                value={selectedTypes}
                onChange={(e) => setSelectedTypes(typeof e.target.value === 'string' ? [] : e.target.value)}
                label="Filter by type"
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {availableTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Box sx={{ flexGrow: 1 }} />
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
            <Tooltip title="Center Graph">
              <IconButton onClick={handleCenter} size="small">
                <CenterIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>

        <Box sx={{ flex: 1, position: 'relative' }}>
          <ForceGraph2D
            ref={graphRef}
            graphData={filteredData}
            nodeLabel="label"
            nodeColor="color"
            linkColor="color"
            nodeRelSize={6}
            linkWidth={2}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
            onNodeClick={handleNodeClick}
            onNodeHover={handleNodeHover}
            backgroundColor={theme.palette.background.paper}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const label = node.label;
              const fontSize = 12/globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;
              const textWidth = ctx.measureText(label).width;
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

              ctx.fillStyle = node.color;
              ctx.beginPath();
              ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
              ctx.fill();

              ctx.fillStyle = theme.palette.background.paper;
              ctx.fillRect(
                node.x - bckgDimensions[0] / 2,
                node.y + 6,
                bckgDimensions[0],
                bckgDimensions[1]
              );

              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = theme.palette.text.primary;
              ctx.fillText(label, node.x, node.y + 6 + fontSize/2);
            }}
          />
        </Box>
      </Paper>

      <Paper
        elevation={2}
        sx={{
          flex: 1,
          p: 2,
          borderRadius: 2,
          bgcolor: theme.palette.background.paper,
          overflow: 'auto'
        }}
      >
        <Typography variant="h6" gutterBottom>
          {hoveredNode ? hoveredNode.label : 'Code Metrics'}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {hoveredNode ? (
            <>
              <Typography variant="subtitle2">Type: {hoveredNode.type}</Typography>
              {hoveredNode.metrics && (
                <>
                  <MetricItem
                    label="Complexity"
                    value={hoveredNode.metrics.complexity || 0}
                    max={1}
                    color={theme.palette.primary.main}
                  />
                  <MetricItem
                    label="Maintainability"
                    value={hoveredNode.metrics.maintainability || 0}
                    max={1}
                    color={theme.palette.secondary.main}
                  />
                </>
              )}
            </>
          ) : (
            <>
              <MetricItem
                label="Complexity"
                value={metrics.complexity}
                max={1}
                color={theme.palette.primary.main}
              />
              <MetricItem
                label="Maintainability"
                value={metrics.maintainability}
                max={1}
                color={theme.palette.secondary.main}
              />
              <MetricItem
                label="Test Coverage"
                value={metrics.testCoverage}
                max={100}
                color={theme.palette.success.main}
              />
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Performance
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Time Complexity: {metrics.performance.timeComplexity}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Space Complexity: {metrics.performance.spaceComplexity}
                </Typography>
              </Box>
            </>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default CodeVisualization;

interface MetricItemProps {
  label: string;
  value: number;
  max: number;
  color: string;
}

const MetricItem: React.FC<MetricItemProps> = ({ label, value, max, color }) => {
  const percentage = (value / max) * 100;
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2" color="textSecondary">
          {value.toFixed(2)}/{max}
        </Typography>
      </Box>
      <Box
        sx={{
          width: '100%',
          height: 4,
          bgcolor: 'grey.200',
          borderRadius: 2,
          overflow: 'hidden'
        }}
      >
        <Box
          sx={{
            width: `${percentage}%`,
            height: '100%',
            bgcolor: color,
            transition: 'width 0.3s ease-in-out'
          }}
        />
      </Box>
    </Box>
  );
}; 