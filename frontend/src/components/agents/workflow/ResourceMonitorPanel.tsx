import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  LinearProgress,
  CircularProgress,
  Tooltip,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Button,
  Menu,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  SelectChangeEvent,
  useTheme,
  alpha
} from '@mui/material';
import {
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  CloudQueue as CloudQueueIcon,
  NetworkCheck as NetworkCheckIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Warning as WarningIcon,
  ErrorOutline as ErrorOutlineIcon,
  FilterList as FilterListIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { Agent, AgentStatus } from '../AgentListPanel';

// Resource types for monitoring
export enum ResourceType {
  CPU = 'CPU',
  MEMORY = 'MEMORY',
  STORAGE = 'STORAGE',
  NETWORK = 'NETWORK',
  API_RATE = 'API_RATE'
}

// Resource usage data interface
export interface ResourceUsage {
  agentId: string;
  timestamp: Date;
  type: ResourceType;
  usage: number; // Percentage (0-100)
  limit: number; // Maximum allowed value
  unit: string; // e.g., 'MB', 'GB', 'req/s'
  current: number; // Current absolute value
}

// System resource interface (global system resources)
export interface SystemResource {
  type: ResourceType;
  usage: number; // Percentage (0-100)
  available: number;
  total: number;
  unit: string;
}

interface ResourceMonitorPanelProps {
  agents: Agent[];
  selectedAgentId?: string;
}

/**
 * Helper function to generate mock resource usage data
 */
const generateMockResourceUsage = (agents: Agent[]): ResourceUsage[] => {
  const resourceUsage: ResourceUsage[] = [];
  const resourceTypes = Object.values(ResourceType);
  const now = new Date();
  
  // Generate a random resource usage entry for each agent and resource type
  agents.forEach(agent => {
    resourceTypes.forEach(type => {
      let usage: number, limit: number, current: number, unit: string;
      
      switch (type) {
        case ResourceType.CPU:
          usage = Math.floor(Math.random() * 100);
          limit = 100;
          current = usage;
          unit = '%';
          break;
        case ResourceType.MEMORY:
          current = Math.floor(Math.random() * 1024) + 256; // 256-1280 MB
          limit = 2048; // 2 GB
          usage = (current / limit) * 100;
          unit = 'MB';
          break;
        case ResourceType.STORAGE:
          current = Math.floor(Math.random() * 5) + 1; // 1-6 GB
          limit = 10; // 10 GB
          usage = (current / limit) * 100;
          unit = 'GB';
          break;
        case ResourceType.NETWORK:
          current = Math.floor(Math.random() * 500) + 50; // 50-550 KB/s
          limit = 1000; // 1000 KB/s
          usage = (current / limit) * 100;
          unit = 'KB/s';
          break;
        case ResourceType.API_RATE:
          current = Math.floor(Math.random() * 90) + 10; // 10-100 req/min
          limit = 120; // 120 req/min
          usage = (current / limit) * 100;
          unit = 'req/min';
          break;
        default:
          usage = Math.floor(Math.random() * 100);
          limit = 100;
          current = usage;
          unit = '%';
      }
      
      resourceUsage.push({
        agentId: agent.id,
        timestamp: now,
        type,
        usage,
        limit,
        current,
        unit
      });
    });
  });
  
  return resourceUsage;
};

/**
 * Helper function to generate mock system resources
 */
const generateMockSystemResources = (): SystemResource[] => {
  const resources: SystemResource[] = [
    {
      type: ResourceType.CPU,
      usage: Math.floor(Math.random() * 70) + 10, // 10-80%
      available: 100 - Math.floor(Math.random() * 70) - 10,
      total: 100,
      unit: '%'
    },
    {
      type: ResourceType.MEMORY,
      usage: Math.floor(Math.random() * 60) + 20, // 20-80%
      available: Math.floor(Math.random() * 8) + 2, // 2-10 GB
      total: 16, // 16 GB
      unit: 'GB'
    },
    {
      type: ResourceType.STORAGE,
      usage: Math.floor(Math.random() * 40) + 10, // 10-50%
      available: Math.floor(Math.random() * 300) + 200, // 200-500 GB
      total: 512, // 512 GB
      unit: 'GB'
    },
    {
      type: ResourceType.NETWORK,
      usage: Math.floor(Math.random() * 50) + 10, // 10-60%
      available: 40, // 40 MB/s
      total: 100, // 100 MB/s
      unit: 'MB/s'
    },
    {
      type: ResourceType.API_RATE,
      usage: Math.floor(Math.random() * 40) + 20, // 20-60%
      available: 400, // 400 req/s
      total: 1000, // 1000 req/s
      unit: 'req/s'
    }
  ];
  
  return resources;
};

/**
 * ResourceMonitorPanel Component - Displays resource usage for agents and system
 */
const ResourceMonitorPanel: React.FC<ResourceMonitorPanelProps> = ({
  agents,
  selectedAgentId
}) => {
  const theme = useTheme();
  
  // Generate mock data
  const [resourceUsage, setResourceUsage] = useState<ResourceUsage[]>(generateMockResourceUsage(agents));
  const [systemResources, setSystemResources] = useState<SystemResource[]>(generateMockSystemResources());
  
  // Filter states
  const [resourceTypeFilter, setResourceTypeFilter] = useState<ResourceType | ''>('');
  const [viewMode, setViewMode] = useState<'detail' | 'summary'>('summary');
  
  // Menu state
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  
  // Format number with unit
  const formatWithUnit = (value: number, unit: string): string => {
    return `${value} ${unit}`;
  };
  
  // Get color based on usage percentage
  const getResourceColor = (usage: number): string => {
    if (usage >= 90) {
      return theme.palette.error.main;
    } else if (usage >= 70) {
      return theme.palette.warning.main;
    } else if (usage >= 50) {
      return theme.palette.info.main;
    } else {
      return theme.palette.success.main;
    }
  };
  
  // Get resource icon
  const getResourceIcon = (type: ResourceType) => {
    switch (type) {
      case ResourceType.CPU:
        return <SpeedIcon />;
      case ResourceType.MEMORY:
        return <MemoryIcon />;
      case ResourceType.STORAGE:
        return <StorageIcon />;
      case ResourceType.NETWORK:
        return <NetworkCheckIcon />;
      case ResourceType.API_RATE:
        return <CloudQueueIcon />;
      default:
        return <SpeedIcon />;
    }
  };
  
  // Get agent resources
  const getAgentResources = (agentId: string): ResourceUsage[] => {
    return resourceUsage.filter(r => r.agentId === agentId);
  };
  
  // Handle refresh
  const handleRefresh = () => {
    setResourceUsage(generateMockResourceUsage(agents));
    setSystemResources(generateMockSystemResources());
  };
  
  // Handle menu open
  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };
  
  // Handle menu close
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };
  
  // Handle resource type filter change
  const handleResourceTypeChange = (event: SelectChangeEvent<ResourceType | ''>) => {
    setResourceTypeFilter(event.target.value as ResourceType | '');
  };
  
  // Get filtered agents list
  const filteredAgents = selectedAgentId 
    ? agents.filter(agent => agent.id === selectedAgentId)
    : agents;
  
  // Render system resources overview
  const renderSystemResources = () => {
    return (
      <Paper elevation={0} variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">System Resources</Typography>
          <IconButton size="small" onClick={handleRefresh}>
            <RefreshIcon />
          </IconButton>
        </Box>
        
        <Grid container spacing={2}>
          {systemResources.map(resource => (
            <Grid item xs={12} sm={6} md={4} key={resource.type}>
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 2, 
                  position: 'relative',
                  bgcolor: alpha(getResourceColor(resource.usage), 0.05),
                  border: `1px solid ${alpha(getResourceColor(resource.usage), 0.2)}`
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ mr: 1, color: getResourceColor(resource.usage) }}>
                    {getResourceIcon(resource.type)}
                  </Box>
                  <Typography variant="subtitle1">{resource.type}</Typography>
                </Box>
                
                <Box sx={{ position: 'relative', mb: 1 }}>
                  <CircularProgress
                    variant="determinate"
                    value={resource.usage}
                    size={80}
                    thickness={4}
                    sx={{ color: getResourceColor(resource.usage) }}
                  />
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="body2" component="div" color="text.secondary">
                      {`${Math.round(resource.usage)}%`}
                    </Typography>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="textSecondary">
                  Available: {formatWithUnit(resource.available, resource.unit)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total: {formatWithUnit(resource.total, resource.unit)}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Paper>
    );
  };
  
  // Render agent resources
  const renderAgentResources = () => {
    if (viewMode === 'summary') {
      return (
        <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Agent</TableCell>
                <TableCell align="center">CPU</TableCell>
                <TableCell align="center">Memory</TableCell>
                <TableCell align="center">Storage</TableCell>
                <TableCell align="center">Network</TableCell>
                <TableCell align="center">API Rate</TableCell>
                <TableCell align="right">Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAgents.map(agent => {
                const agentResources = getAgentResources(agent.id);
                const cpuResource = agentResources.find(r => r.type === ResourceType.CPU);
                const memoryResource = agentResources.find(r => r.type === ResourceType.MEMORY);
                const storageResource = agentResources.find(r => r.type === ResourceType.STORAGE);
                const networkResource = agentResources.find(r => r.type === ResourceType.NETWORK);
                const apiRateResource = agentResources.find(r => r.type === ResourceType.API_RATE);
                
                return (
                  <TableRow key={agent.id}>
                    <TableCell>{agent.name}</TableCell>
                    <TableCell align="center">
                      {cpuResource && (
                        <Tooltip title={`${cpuResource.current}${cpuResource.unit}`}>
                          <LinearProgress
                            variant="determinate"
                            value={cpuResource.usage}
                            color={cpuResource.usage > 90 ? 'error' : cpuResource.usage > 70 ? 'warning' : 'primary'}
                            sx={{ height: 8, borderRadius: 1, minWidth: 50 }}
                          />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {memoryResource && (
                        <Tooltip title={`${memoryResource.current}${memoryResource.unit} / ${memoryResource.limit}${memoryResource.unit}`}>
                          <LinearProgress
                            variant="determinate"
                            value={memoryResource.usage}
                            color={memoryResource.usage > 90 ? 'error' : memoryResource.usage > 70 ? 'warning' : 'primary'}
                            sx={{ height: 8, borderRadius: 1, minWidth: 50 }}
                          />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {storageResource && (
                        <Tooltip title={`${storageResource.current}${storageResource.unit} / ${storageResource.limit}${storageResource.unit}`}>
                          <LinearProgress
                            variant="determinate"
                            value={storageResource.usage}
                            color={storageResource.usage > 90 ? 'error' : storageResource.usage > 70 ? 'warning' : 'primary'}
                            sx={{ height: 8, borderRadius: 1, minWidth: 50 }}
                          />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {networkResource && (
                        <Tooltip title={`${networkResource.current}${networkResource.unit} / ${networkResource.limit}${networkResource.unit}`}>
                          <LinearProgress
                            variant="determinate"
                            value={networkResource.usage}
                            color={networkResource.usage > 90 ? 'error' : networkResource.usage > 70 ? 'warning' : 'primary'}
                            sx={{ height: 8, borderRadius: 1, minWidth: 50 }}
                          />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {apiRateResource && (
                        <Tooltip title={`${apiRateResource.current}${apiRateResource.unit} / ${apiRateResource.limit}${apiRateResource.unit}`}>
                          <LinearProgress
                            variant="determinate"
                            value={apiRateResource.usage}
                            color={apiRateResource.usage > 90 ? 'error' : apiRateResource.usage > 70 ? 'warning' : 'primary'}
                            sx={{ height: 8, borderRadius: 1, minWidth: 50 }}
                          />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={agent.status}
                        size="small"
                        color={
                          agent.status === AgentStatus.ACTIVE || agent.status === AgentStatus.PROCESSING
                            ? 'success'
                            : agent.status === AgentStatus.WARNING
                            ? 'warning'
                            : agent.status === AgentStatus.ERROR
                            ? 'error'
                            : 'default'
                        }
                        variant="outlined"
                      />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      );
    } else {
      // Detailed view
      return (
        <Box>
          {filteredAgents.map(agent => {
            const agentResources = getAgentResources(agent.id);
            
            // Filter by resource type if selected
            const filteredResources = resourceTypeFilter
              ? agentResources.filter(r => r.type === resourceTypeFilter)
              : agentResources;
              
            if (filteredResources.length === 0) return null;
            
            return (
              <Paper elevation={0} variant="outlined" sx={{ p: 2, mb: 2 }} key={agent.id}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">{agent.name}</Typography>
                  <Chip
                    label={agent.status}
                    size="small"
                    color={
                      agent.status === AgentStatus.ACTIVE || agent.status === AgentStatus.PROCESSING
                        ? 'success'
                        : agent.status === AgentStatus.WARNING
                        ? 'warning'
                        : agent.status === AgentStatus.ERROR
                        ? 'error'
                        : 'default'
                    }
                  />
                </Box>
                
                <Grid container spacing={2}>
                  {filteredResources.map(resource => (
                    <Grid item xs={12} sm={6} md={4} key={resource.type}>
                      <Paper 
                        elevation={0} 
                        sx={{ 
                          p: 2, 
                          bgcolor: alpha(getResourceColor(resource.usage), 0.05),
                          border: `1px solid ${alpha(getResourceColor(resource.usage), 0.2)}`
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Box sx={{ mr: 1, color: getResourceColor(resource.usage) }}>
                            {getResourceIcon(resource.type)}
                          </Box>
                          <Typography variant="body1">{resource.type}</Typography>
                        </Box>
                        
                        <LinearProgress
                          variant="determinate"
                          value={resource.usage}
                          color={resource.usage > 90 ? 'error' : resource.usage > 70 ? 'warning' : 'primary'}
                          sx={{ height: 10, borderRadius: 1, mb: 1 }}
                        />
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="textSecondary">
                            {formatWithUnit(resource.current, resource.unit)}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {`${Math.round(resource.usage)}%`}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {formatWithUnit(resource.limit, resource.unit)}
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            );
          })}
        </Box>
      );
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with controls */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Resource Monitor
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel id="resource-type-label">Resource Type</InputLabel>
            <Select
              labelId="resource-type-label"
              id="resource-type"
              value={resourceTypeFilter}
              onChange={handleResourceTypeChange}
              label="Resource Type"
            >
              <MenuItem value="">All Resources</MenuItem>
              {Object.values(ResourceType).map(type => (
                <MenuItem value={type} key={type}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ mr: 1 }}>{getResourceIcon(type)}</Box>
                    {type}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            size="small"
            startIcon={viewMode === 'summary' ? <TimelineIcon /> : <FilterListIcon />}
            onClick={() => setViewMode(viewMode === 'summary' ? 'detail' : 'summary')}
          >
            {viewMode === 'summary' ? 'Detailed View' : 'Summary View'}
          </Button>
          
          <IconButton onClick={handleMenuOpen} size="small">
            <MoreVertIcon />
          </IconButton>
        </Box>
      </Box>
      
      {/* Main content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {/* System resources section */}
        {renderSystemResources()}
        
        {/* Agent resources section */}
        <Typography variant="h6" sx={{ mb: 2 }}>Agent Resources</Typography>
        {filteredAgents.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <Typography variant="body2" color="textSecondary">
              No agents selected or available
            </Typography>
          </Box>
        ) : (
          renderAgentResources()
        )}
      </Box>
      
      {/* Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon fontSize="small" sx={{ mr: 1 }} />
          Refresh Data
        </MenuItem>
        <MenuItem onClick={() => {
          handleMenuClose();
          setResourceTypeFilter('');
        }}>
          <FilterListIcon fontSize="small" sx={{ mr: 1 }} />
          Clear Filters
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ResourceMonitorPanel;
