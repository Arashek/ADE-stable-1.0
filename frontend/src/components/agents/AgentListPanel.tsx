import React, { useState } from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Typography,
  Divider,
  Chip,
  TextField,
  InputAdornment,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  useTheme,
  Badge,
  Button
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import MemoryIcon from '@mui/icons-material/Memory';
import DesignServicesIcon from '@mui/icons-material/DesignServices';
import ArchitectureIcon from '@mui/icons-material/Architecture';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

// Agent status types
export enum AgentStatus {
  ACTIVE = 'active',
  IDLE = 'idle',
  WARNING = 'warning',
  ERROR = 'error',
  PROCESSING = 'processing'
}

// Agent types
export enum AgentType {
  VALIDATOR = 'validator',
  DESIGNER = 'designer',
  ARCHITECT = 'architect',
  SECURITY = 'security',
  PERFORMANCE = 'performance',
  ADMIN = 'admin'
}

// Agent interface
export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  currentTask?: string;
  lastActive: Date;
  cpuUsage: number;
  memoryUsage: number;
}

// Props for the AgentListPanel component
interface AgentListPanelProps {
  agents: Agent[];
  selectedAgentId?: string;
  onAgentSelect: (agentId: string) => void;
}

/**
 * Agent List Panel Component - Displays all active agents with their statuses
 */
const AgentListPanel: React.FC<AgentListPanelProps> = ({ 
  agents, 
  selectedAgentId, 
  onAgentSelect 
}) => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [statusFilters, setStatusFilters] = useState<AgentStatus[]>([]);
  const [typeFilters, setTypeFilters] = useState<AgentType[]>([]);
  const [contextMenuAnchorEl, setContextMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [contextMenuAgentId, setContextMenuAgentId] = useState<string | null>(null);

  // Handle search query change
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  // Handle filter menu open
  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  // Handle filter menu close
  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  // Handle context menu open
  const handleContextMenu = (event: React.MouseEvent<HTMLElement>, agentId: string) => {
    event.preventDefault();
    event.stopPropagation();
    setContextMenuAnchorEl(event.currentTarget);
    setContextMenuAgentId(agentId);
  };

  // Handle context menu close
  const handleContextMenuClose = () => {
    setContextMenuAnchorEl(null);
    setContextMenuAgentId(null);
  };

  // Toggle status filter
  const toggleStatusFilter = (status: AgentStatus) => {
    setStatusFilters(prev => 
      prev.includes(status) 
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  };

  // Toggle type filter
  const toggleTypeFilter = (type: AgentType) => {
    setTypeFilters(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  // Filter agents based on search query and filters
  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          agent.type.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatusFilter = statusFilters.length === 0 || statusFilters.includes(agent.status);
    const matchesTypeFilter = typeFilters.length === 0 || typeFilters.includes(agent.type);
    
    return matchesSearch && matchesStatusFilter && matchesTypeFilter;
  });

  // Get agent icon based on type
  const getAgentIcon = (type: AgentType) => {
    switch (type) {
      case AgentType.VALIDATOR:
        return <MemoryIcon />;
      case AgentType.DESIGNER:
        return <DesignServicesIcon />;
      case AgentType.ARCHITECT:
        return <ArchitectureIcon />;
      case AgentType.SECURITY:
        return <SecurityIcon />;
      case AgentType.PERFORMANCE:
        return <SpeedIcon />;
      case AgentType.ADMIN:
        return <AdminPanelSettingsIcon />;
      default:
        return <MemoryIcon />;
    }
  };

  // Get status color based on agent status
  const getStatusColor = (status: AgentStatus) => {
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
  };

  // Get type color based on agent type
  const getTypeColor = (type: AgentType) => {
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
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Search and filter header */}
      <Box sx={{ mb: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search agents..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <Tooltip title="Filter agents">
                  <IconButton 
                    size="small" 
                    onClick={handleFilterClick}
                    color={statusFilters.length > 0 || typeFilters.length > 0 ? "primary" : "default"}
                  >
                    <Badge 
                      color="primary" 
                      badgeContent={statusFilters.length + typeFilters.length} 
                      invisible={statusFilters.length + typeFilters.length === 0}
                    >
                      <FilterListIcon fontSize="small" />
                    </Badge>
                  </IconButton>
                </Tooltip>
              </InputAdornment>
            ),
          }}
          sx={{ mb: 1 }}
        />

        {/* Filter chips display */}
        {(statusFilters.length > 0 || typeFilters.length > 0) && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
            {statusFilters.map(status => (
              <Chip
                key={status}
                label={status.charAt(0).toUpperCase() + status.slice(1)}
                size="small"
                onDelete={() => toggleStatusFilter(status)}
                sx={{ 
                  bgcolor: getStatusColor(status),
                  color: theme.palette.getContrastText(getStatusColor(status)),
                  '& .MuiChip-deleteIcon': {
                    color: theme.palette.getContrastText(getStatusColor(status))
                  }
                }}
              />
            ))}
            {typeFilters.map(type => (
              <Chip
                key={type}
                label={type.charAt(0).toUpperCase() + type.slice(1)}
                size="small"
                onDelete={() => toggleTypeFilter(type)}
                sx={{ 
                  bgcolor: getTypeColor(type),
                  color: theme.palette.getContrastText(getTypeColor(type)),
                  '& .MuiChip-deleteIcon': {
                    color: theme.palette.getContrastText(getTypeColor(type))
                  }
                }}
              />
            ))}
          </Box>
        )}
      </Box>

      {/* Agent list */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {filteredAgents.length > 0 ? (
          <List dense disablePadding>
            {filteredAgents.map((agent) => (
              <React.Fragment key={agent.id}>
                <ListItemButton
                  selected={selectedAgentId === agent.id}
                  onClick={() => onAgentSelect(agent.id)}
                  onContextMenu={(e) => handleContextMenu(e, agent.id)}
                  sx={{
                    borderLeft: '3px solid',
                    borderLeftColor: getStatusColor(agent.status),
                    transition: 'all 0.2s',
                    '&:hover': {
                      bgcolor: theme.palette.action.hover,
                    },
                    '&.Mui-selected': {
                      bgcolor: theme.palette.action.selected,
                      '&:hover': {
                        bgcolor: theme.palette.action.selected,
                      },
                    },
                    position: 'relative',
                    ...(agent.status === AgentStatus.PROCESSING && {
                      animation: 'pulse 2s infinite',
                      '@keyframes pulse': {
                        '0%': {
                          boxShadow: '0 0 0 0 rgba(33, 150, 243, 0.4)'
                        },
                        '70%': {
                          boxShadow: '0 0 0 10px rgba(33, 150, 243, 0)'
                        },
                        '100%': {
                          boxShadow: '0 0 0 0 rgba(33, 150, 243, 0)'
                        }
                      }
                    })
                  }}
                >
                  <ListItemIcon sx={{ color: getTypeColor(agent.type) }}>
                    {getAgentIcon(agent.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" fontWeight={500}>
                        {agent.name}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                        {agent.currentTask ? 
                          `Working on: ${agent.currentTask.length > 20 ? 
                            agent.currentTask.substring(0, 20) + '...' : 
                            agent.currentTask}`
                          : 'No active task'
                        }
                      </Typography>
                    }
                  />
                  <Tooltip title={`Status: ${agent.status}`}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        bgcolor: getStatusColor(agent.status),
                        ...(agent.status === AgentStatus.PROCESSING && {
                          animation: 'pulse-status 1.5s infinite',
                          '@keyframes pulse-status': {
                            '0%': {
                              opacity: 1
                            },
                            '50%': {
                              opacity: 0.4
                            },
                            '100%': {
                              opacity: 1
                            }
                          }
                        })
                      }}
                    />
                  </Tooltip>
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleContextMenu(e, agent.id);
                    }}
                    sx={{ ml: 1 }}
                  >
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </ListItemButton>
                <Divider variant="inset" component="li" />
              </React.Fragment>
            ))}
          </List>
        ) : (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              No agents match your search criteria
            </Typography>
          </Box>
        )}
      </Box>

      {/* Add new agent button */}
      <Box sx={{ pt: 1 }}>
        <Button
          variant="outlined"
          fullWidth
          startIcon={<AddIcon />}
          size="small"
        >
          Add Agent
        </Button>
      </Box>

      {/* Filter menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleFilterClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Typography variant="subtitle2" sx={{ px: 2, py: 1 }}>
          Filter by Status
        </Typography>
        <MenuItem dense onClick={() => toggleStatusFilter(AgentStatus.ACTIVE)}>
          <ListItemIcon>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: getStatusColor(AgentStatus.ACTIVE),
              }}
            />
          </ListItemIcon>
          <ListItemText>Active</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleStatusFilter(AgentStatus.IDLE)}>
          <ListItemIcon>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: getStatusColor(AgentStatus.IDLE),
              }}
            />
          </ListItemIcon>
          <ListItemText>Idle</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleStatusFilter(AgentStatus.WARNING)}>
          <ListItemIcon>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: getStatusColor(AgentStatus.WARNING),
              }}
            />
          </ListItemIcon>
          <ListItemText>Warning</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleStatusFilter(AgentStatus.ERROR)}>
          <ListItemIcon>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: getStatusColor(AgentStatus.ERROR),
              }}
            />
          </ListItemIcon>
          <ListItemText>Error</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleStatusFilter(AgentStatus.PROCESSING)}>
          <ListItemIcon>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: getStatusColor(AgentStatus.PROCESSING),
              }}
            />
          </ListItemIcon>
          <ListItemText>Processing</ListItemText>
        </MenuItem>
        <Divider />
        <Typography variant="subtitle2" sx={{ px: 2, py: 1 }}>
          Filter by Type
        </Typography>
        <MenuItem dense onClick={() => toggleTypeFilter(AgentType.VALIDATOR)}>
          <ListItemIcon sx={{ color: getTypeColor(AgentType.VALIDATOR) }}>
            <MemoryIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Validator</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleTypeFilter(AgentType.DESIGNER)}>
          <ListItemIcon sx={{ color: getTypeColor(AgentType.DESIGNER) }}>
            <DesignServicesIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Designer</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleTypeFilter(AgentType.ARCHITECT)}>
          <ListItemIcon sx={{ color: getTypeColor(AgentType.ARCHITECT) }}>
            <ArchitectureIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Architect</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleTypeFilter(AgentType.SECURITY)}>
          <ListItemIcon sx={{ color: getTypeColor(AgentType.SECURITY) }}>
            <SecurityIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Security</ListItemText>
        </MenuItem>
        <MenuItem dense onClick={() => toggleTypeFilter(AgentType.PERFORMANCE)}>
          <ListItemIcon sx={{ color: getTypeColor(AgentType.PERFORMANCE) }}>
            <SpeedIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Performance</ListItemText>
        </MenuItem>
      </Menu>

      {/* Context menu for agent actions */}
      <Menu
        anchorEl={contextMenuAnchorEl}
        open={Boolean(contextMenuAnchorEl)}
        onClose={handleContextMenuClose}
      >
        <MenuItem onClick={handleContextMenuClose}>
          <ListItemIcon>
            <RefreshIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Restart Agent</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleContextMenuClose}>
          <ListItemIcon>
            <SecurityIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Logs</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleContextMenuClose}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Configure</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

// Generate some mock agents for testing
export const generateMockAgents = (count: number = 5): Agent[] => {
  const statuses = Object.values(AgentStatus);
  const types = Object.values(AgentType);
  const agents: Agent[] = [];

  for (let i = 0; i < count; i++) {
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    const randomType = types[Math.floor(Math.random() * types.length)];
    
    agents.push({
      id: `agent-${i}`,
      name: `${randomType.charAt(0).toUpperCase() + randomType.slice(1)} Agent ${i + 1}`,
      type: randomType,
      status: randomStatus,
      currentTask: randomStatus === AgentStatus.IDLE ? undefined : `Task ${i + 1} processing...`,
      lastActive: new Date(Date.now() - Math.floor(Math.random() * 1000000)),
      cpuUsage: Math.floor(Math.random() * 100),
      memoryUsage: Math.floor(Math.random() * 100)
    });
  }

  return agents;
};

export default AgentListPanel;
