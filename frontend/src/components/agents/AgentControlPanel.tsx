import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  ButtonGroup,
  Divider,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Grid,
  Stack,
  useTheme,
  alpha,
  SelectChangeEvent
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  SaveAlt as SaveAltIcon,
  Settings as SettingsIcon,
  Pause as PauseIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  BugReport as BugReportIcon,
  Sync as SyncIcon,
  Cloud as CloudIcon,
  CloudDownload as CloudDownloadIcon,
  SystemUpdateAlt as SystemUpdateAltIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';
import { Agent, AgentStatus, AgentType } from './AgentListPanel';

interface AgentControlPanelProps {
  agents: Agent[];
  onStartAll?: () => void;
  onStopAll?: () => void;
  onRefreshStatus?: () => void;
  onResetAgents?: () => void;
  onAddAgent?: (agentData: Partial<Agent>) => void;
  onRemoveAgent?: (agentId: string) => void;
  onUpdateAgent?: (agentId: string, agentData: Partial<Agent>) => void;
  onExportConfig?: () => void;
  onImportConfig?: (config: string) => void;
  onSystemAction?: (action: string, params?: any) => void;
}

/**
 * AgentControlPanel Component - Provides system-wide actions for managing the agent network
 */
const AgentControlPanel: React.FC<AgentControlPanelProps> = ({
  agents,
  onStartAll,
  onStopAll,
  onRefreshStatus,
  onResetAgents,
  onAddAgent,
  onRemoveAgent,
  onUpdateAgent,
  onExportConfig,
  onImportConfig,
  onSystemAction
}) => {
  const theme = useTheme();
  
  // States for dialog controls
  const [addAgentDialogOpen, setAddAgentDialogOpen] = useState(false);
  const [newAgentData, setNewAgentData] = useState<Partial<Agent>>({
    name: '',
    type: AgentType.DESIGNER,
    status: AgentStatus.IDLE
  });
  
  // State for confirmation dialog
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [confirmDialogAction, setConfirmDialogAction] = useState<{
    title: string;
    content: string;
    action: () => void;
  }>({ title: '', content: '', action: () => {} });
  
  // State for more actions menu
  const [moreActionsAnchorEl, setMoreActionsAnchorEl] = useState<null | HTMLElement>(null);
  const moreActionsMenuOpen = Boolean(moreActionsAnchorEl);
  
  // System status summary
  const activeAgents = agents.filter(agent => agent.status === AgentStatus.ACTIVE || agent.status === AgentStatus.PROCESSING).length;
  const errorAgents = agents.filter(agent => agent.status === AgentStatus.ERROR).length;
  const warningAgents = agents.filter(agent => agent.status === AgentStatus.WARNING).length;
  
  // Handle agent creation
  const handleAddAgent = () => {
    if (newAgentData.name && newAgentData.type) {
      onAddAgent && onAddAgent({
        ...newAgentData,
        id: `agent-${Date.now()}`, // Generate a temporary ID
        status: AgentStatus.IDLE // Always start as idle
      });
      setAddAgentDialogOpen(false);
      // Reset form
      setNewAgentData({
        name: '',
        type: AgentType.DESIGNER,
        status: AgentStatus.IDLE
      });
    }
  };
  
  // Handle agent type change
  const handleAgentTypeChange = (event: SelectChangeEvent<AgentType>) => {
    setNewAgentData({
      ...newAgentData,
      type: event.target.value as AgentType
    });
  };
  
  // Handle confirmation dialog open
  const openConfirmDialog = (title: string, content: string, action: () => void) => {
    setConfirmDialogAction({ title, content, action });
    setConfirmDialogOpen(true);
  };
  
  // Handle more actions menu open
  const handleMoreActionsClick = (event: React.MouseEvent<HTMLElement>) => {
    setMoreActionsAnchorEl(event.currentTarget);
  };
  
  // Handle more actions menu close
  const handleMoreActionsClose = () => {
    setMoreActionsAnchorEl(null);
  };
  
  // Handle export configuration
  const handleExportConfig = () => {
    onExportConfig && onExportConfig();
    handleMoreActionsClose();
  };
  
  // Handle import configuration
  const handleImportConfigClick = () => {
    // This would typically open a file dialog
    handleMoreActionsClose();
    
    // Mock implementation - in a real app, this would use a file input
    const mockConfig = JSON.stringify({ agents: agents.map(a => ({ id: a.id, name: a.name, type: a.type })) });
    onImportConfig && onImportConfig(mockConfig);
  };
  
  // Handle system diagnostics
  const handleSystemDiagnostics = () => {
    onSystemAction && onSystemAction('diagnostics');
    handleMoreActionsClose();
  };
  
  // Handle cloud sync
  const handleCloudSync = () => {
    onSystemAction && onSystemAction('cloudSync');
    handleMoreActionsClose();
  };
  
  // Handle system update
  const handleSystemUpdate = () => {
    openConfirmDialog(
      'Update System',
      'Are you sure you want to update the agent system? This might interrupt ongoing tasks.',
      () => {
        onSystemAction && onSystemAction('update');
        handleMoreActionsClose();
      }
    );
  };

  return (
    <Box>
      {/* Main control buttons */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={6}>
          <ButtonGroup variant="contained" fullWidth>
            <Button 
              color="primary" 
              startIcon={<PlayArrowIcon />}
              onClick={onStartAll}
              sx={{ flex: 1 }}
            >
              Start All
            </Button>
            <Button 
              color="secondary" 
              startIcon={<PauseIcon />}
              onClick={onStopAll}
              sx={{ flex: 1 }}
            >
              Pause All
            </Button>
            <Button 
              color="error" 
              startIcon={<StopIcon />}
              onClick={() => openConfirmDialog(
                'Stop All Agents',
                'Are you sure you want to stop all agents? This will terminate all ongoing tasks.',
                () => onStopAll && onStopAll()
              )}
              sx={{ flex: 1 }}
            >
              Stop All
            </Button>
          </ButtonGroup>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ButtonGroup variant="outlined" fullWidth>
            <Button 
              startIcon={<RefreshIcon />}
              onClick={onRefreshStatus}
              sx={{ flex: 1 }}
            >
              Refresh Status
            </Button>
            <Button 
              startIcon={<SyncIcon />}
              onClick={() => openConfirmDialog(
                'Reset Agents',
                'Are you sure you want to reset all agents to their initial state? This will clear all agent memory and state.',
                () => onResetAgents && onResetAgents()
              )}
              sx={{ flex: 1 }}
            >
              Reset Agents
            </Button>
            <Button 
              startIcon={<AddIcon />}
              onClick={() => setAddAgentDialogOpen(true)}
              sx={{ flex: 1 }}
            >
              Add Agent
            </Button>
            
            {/* More actions menu button */}
            <Tooltip title="More actions">
              <IconButton
                onClick={handleMoreActionsClick}
                size="small"
                aria-controls={moreActionsMenuOpen ? 'more-actions-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={moreActionsMenuOpen ? 'true' : undefined}
              >
                <MoreVertIcon />
              </IconButton>
            </Tooltip>
          </ButtonGroup>
        </Grid>
      </Grid>
      
      {/* System status summary */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 2, 
          mb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          bgcolor: alpha(theme.palette.primary.main, 0.05)
        }}
      >
        <Typography variant="subtitle2">
          System Status
        </Typography>
        
        <Stack direction="row" spacing={2}>
          <Chip 
            icon={<PlayArrowIcon fontSize="small" />} 
            label={`${activeAgents} Active`}
            size="small"
            color="primary"
            variant={activeAgents > 0 ? "filled" : "outlined"}
          />
          
          <Chip 
            icon={<WarningIcon fontSize="small" />} 
            label={`${warningAgents} Warnings`}
            size="small"
            color="warning"
            variant={warningAgents > 0 ? "filled" : "outlined"}
          />
          
          <Chip 
            icon={<ErrorIcon fontSize="small" />} 
            label={`${errorAgents} Errors`}
            size="small"
            color="error"
            variant={errorAgents > 0 ? "filled" : "outlined"}
          />
          
          <Chip 
            icon={<CloudIcon fontSize="small" />} 
            label="Cloud: Ready"
            size="small"
            color="info"
            variant="outlined"
          />
        </Stack>
      </Paper>
      
      {/* Quick actions */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 2, 
          bgcolor: alpha(theme.palette.background.paper, 0.6)
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          Quick Actions
        </Typography>
        
        <Grid container spacing={1}>
          <Grid item xs={4}>
            <Button 
              variant="outlined" 
              color="primary"
              startIcon={<BugReportIcon />}
              fullWidth
              size="small"
              onClick={handleSystemDiagnostics}
            >
              Diagnostics
            </Button>
          </Grid>
          
          <Grid item xs={4}>
            <Button 
              variant="outlined" 
              color="primary"
              startIcon={<CloudDownloadIcon />}
              fullWidth
              size="small"
              onClick={handleCloudSync}
            >
              Cloud Sync
            </Button>
          </Grid>
          
          <Grid item xs={4}>
            <Button 
              variant="outlined" 
              color="primary"
              startIcon={<SettingsIcon />}
              fullWidth
              size="small"
              onClick={() => onSystemAction && onSystemAction('settings')}
            >
              Settings
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* More actions menu */}
      <Menu
        id="more-actions-menu"
        anchorEl={moreActionsAnchorEl}
        open={moreActionsMenuOpen}
        onClose={handleMoreActionsClose}
        MenuListProps={{
          'aria-labelledby': 'more-actions-button',
        }}
      >
        <MenuItem onClick={handleExportConfig}>
          <ListItemIcon>
            <SaveAltIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Configuration</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleImportConfigClick}>
          <ListItemIcon>
            <CloudDownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Import Configuration</ListItemText>
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={handleSystemDiagnostics}>
          <ListItemIcon>
            <BugReportIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Run System Diagnostics</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleCloudSync}>
          <ListItemIcon>
            <CloudIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Cloud Sync</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleSystemUpdate}>
          <ListItemIcon>
            <SystemUpdateAltIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Check for Updates</ListItemText>
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={() => {
          openConfirmDialog(
            'Delete All Agents',
            'Are you sure you want to delete all agents? This action cannot be undone.',
            () => {
              agents.forEach(agent => {
                onRemoveAgent && onRemoveAgent(agent.id);
              });
              handleMoreActionsClose();
            }
          );
        }}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText primary="Delete All Agents" primaryTypographyProps={{ color: 'error' }} />
        </MenuItem>
      </Menu>
      
      {/* Add Agent Dialog */}
      <Dialog 
        open={addAgentDialogOpen} 
        onClose={() => setAddAgentDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add New Agent</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Configure the new agent properties below. Each agent must have a unique name and specific type.
          </DialogContentText>
          
          <TextField
            autoFocus
            margin="dense"
            id="agent-name"
            label="Agent Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newAgentData.name}
            onChange={(e) => setNewAgentData({ ...newAgentData, name: e.target.value })}
            sx={{ mt: 2, mb: 2 }}
            required
          />
          
          <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
            <InputLabel id="agent-type-label">Agent Type</InputLabel>
            <Select
              labelId="agent-type-label"
              id="agent-type"
              value={newAgentData.type}
              onChange={handleAgentTypeChange}
              label="Agent Type"
              required
            >
              <MenuItem value={AgentType.VALIDATOR}>Validator</MenuItem>
              <MenuItem value={AgentType.DESIGNER}>Designer</MenuItem>
              <MenuItem value={AgentType.ARCHITECT}>Architect</MenuItem>
              <MenuItem value={AgentType.SECURITY}>Security</MenuItem>
              <MenuItem value={AgentType.PERFORMANCE}>Performance</MenuItem>
              <MenuItem value={AgentType.ADMIN}>Admin</MenuItem>
            </Select>
          </FormControl>
          
          <DialogContentText variant="caption">
            Note: New agents will be created in the idle state and can be activated after creation.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddAgentDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAddAgent}
            variant="contained"
            disabled={!newAgentData.name || !newAgentData.type}
          >
            Add Agent
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
      >
        <DialogTitle>{confirmDialogAction.title}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {confirmDialogAction.content}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => {
              confirmDialogAction.action();
              setConfirmDialogOpen(false);
            }} 
            variant="contained" 
            color="primary"
            autoFocus
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentControlPanel;
