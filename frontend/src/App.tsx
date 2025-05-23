import React, { useState, useEffect, Suspense } from 'react';
import {
  Box,
  Paper,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CssBaseline,
  Divider,
  Tooltip,
  Badge,
  Menu,
  MenuItem,
  Button,
  Fab,
  useMediaQuery,
  ButtonGroup,
  Chip,
  Snackbar,
  Alert,
  AlertColor,
  Grid,
  CircularProgress,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Code as CodeIcon,
  Palette as DesignIcon,
  Psychology as AIIcon,
  Build as ToolsIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Chat as ChatIcon,
  Notifications as NotificationsIcon,
  Terminal as TerminalIcon,
  Assessment as AnalyticsIcon,
  BugReport as BugReportIcon,
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Close as CloseIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Security as SecurityIcon,
  ExpandMore as ExpandMoreIcon,
  Insights as AdvisorIcon,
  PlayArrow as RunIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Storage as DataIcon,
  InsertChart as InsightsIcon,
} from '@mui/icons-material';
import { styled, useTheme, alpha } from '@mui/material/styles';
import { createTheme, Theme } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import axios from 'axios';

// Define prop interfaces for styled components
interface AppBarStyledProps {
  open?: boolean;
}

interface MainProps {
  open?: boolean;
}

interface TaskProgressBarProps {
  progress?: number;
}

import CommandHub from './components/CommandHub';
import LiveChat from './components/LiveChat';
import { LoadingStates } from './components/common/LoadingStates';
import { GestureControls } from './components/common/GestureControls';
import { TransitionWrapper } from './components/common/TransitionWrapper';
import Layout from './components/Layout';
import Home from './routes/Home';
import ModelDashboard from './components/ModelDashboard';
import Settings from './routes/Settings';
import errorLogger from './services/errorLogging';
import TestApi from './TestApi';
import PromptProcessor from './components/PromptProcessor';
import ErrorMonitoringDashboard from './components/ErrorMonitoringDashboard';
import ConsoleCapture from './components/debug/ConsoleCapture';
import DiagnosticPanel from './components/DiagnosticPanel';
import PydanticTester from './components/PydanticTester';
import SimpleDiagnostic from './components/SimpleDiagnostic';
import ErrorBoundary from './components/ErrorBoundary';

// Mission Control theme styling
const drawerWidth = 260;

const openedMixin = (theme: Theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
  backgroundColor: theme.palette.background.default,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.05)}`,
});

const closedMixin = (theme: Theme) => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: theme.spacing(7),
  backgroundColor: theme.palette.background.default,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.05)}`,
});

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

const AppBarStyled = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<AppBarStyledProps>(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  boxShadow: 'none',
  backdropFilter: 'blur(8px)',
  backgroundColor: alpha(theme.palette.background.default, 0.8),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

interface MainProps {
  open?: boolean;
}

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<MainProps>(
  ({ theme, open }) => ({
    flexGrow: 1,
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: 0,
    ...(open && {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
    }),
  }),
);

const StatusBar = styled(Box)(({ theme }) => ({
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  padding: theme.spacing(0.5, 2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  backgroundColor: alpha(theme.palette.background.default, 0.8),
  backdropFilter: 'blur(8px)',
}));

const TaskProgressBar = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'progress',
})<TaskProgressBarProps>(({ theme, progress = 0 }) => ({
  position: 'relative',
  height: '3px',
  width: '100%',
  backgroundColor: alpha(theme.palette.divider, 0.2),
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    height: '100%',
    width: `${progress}%`,
    backgroundColor: theme.palette.primary.main,
    transition: 'width 0.4s ease-in-out'
  }
}));

const navigation = [
  { name: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { name: 'Command Hub', icon: <TerminalIcon />, path: '/command-hub' },
  { name: 'Design Hub', icon: <DesignIcon />, path: '/design-hub' },
  { name: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

// Error boundary wrapper for routes
const ProtectedRoute = ({ children }) => {
  // This would normally check authentication status
  const isAuthenticated = true;
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  return <ErrorBoundary componentName="ProtectedRoute">{children}</ErrorBoundary>;
};

function App() {
  const [open, setOpen] = useState(true);
  const [activeAgent, setActiveAgent] = useState('assistant'); // assistant, designer, developer, or advisor
  const [isGenerating, setIsGenerating] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [notificationsCount, setNotificationsCount] = useState(3);
  const [currentProject, setCurrentProject] = useState('ADE Frontend');
  const [buildProgress, setBuildProgress] = useState(0);
  const [systemStatus, setSystemStatus] = useState('idle');
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertSeverity, setAlertSeverity] = useState<AlertColor>('info');
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Auto-close drawer on mobile
  useEffect(() => {
    if (isMobile) {
      setOpen(false);
    } else {
      setOpen(true);
    }
  }, [isMobile]);

  // Simulate agent communication and progress for demo
  useEffect(() => {
    if (isGenerating) {
      const interval = setInterval(() => {
        setBuildProgress(prev => {
          const newProgress = prev + Math.random() * 5;
          if (newProgress >= 100) {
            clearInterval(interval);
            setIsGenerating(false);
            setSystemStatus('completed');
            showAlert('MVP successfully built! Check the generated code.', 'success');
            return 100;
          }
          return newProgress;
        });
      }, 500);
      
      return () => clearInterval(interval);
    }
  }, [isGenerating]);

  useEffect(() => {
    axios.get('/api/health')
      .then(response => console.log('Backend connection:', response.data))
      .catch(error => console.error('Backend connection failed:', error));
  }, []);

  const showAlert = (message: string, severity: AlertColor = 'info') => {
    setAlertMessage(message);
    setAlertSeverity(severity);
    setAlertOpen(true);
  };

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleDesignSave = (design) => {
    console.log('Design saved:', design);
    showAlert('Design saved successfully', 'success');
  };

  const handleCodeGeneration = async (design) => {
    setIsGenerating(true);
    setSystemStatus('building');
    showAlert('Build process started. Agents are generating your MVP...', 'info');
    setBuildProgress(0);
    
    // Actual code generation would trigger backend communication here
  };

  const handleStopGeneration = () => {
    setIsGenerating(false);
    setSystemStatus('stopped');
    setBuildProgress(0);
    showAlert('Build process stopped', 'warning');
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleToggleChatPanel = () => {
    setChatOpen(!chatOpen);
  };

  const handleAgentSwitch = (agent) => {
    setActiveAgent(agent);
    showAlert(`Switched to ${agent.charAt(0).toUpperCase() + agent.slice(1)} Agent`, 'info');
    handleMenuClose();
  };

  const handleThemeToggle = () => {
    setDarkMode(!darkMode);
  };

  const handleAgentSelect = (agentId) => {
    const agentType = agentId.split('-')[0];
    handleAgentSwitch(agentType);
  };

  return (
    <Router>
      <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
        <AppBarStyled position="fixed" open={open} color="transparent">
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="toggle drawer"
              onClick={handleDrawerToggle}
              edge="start"
              sx={{ mr: 2 }}
            >
              {open ? <ChevronLeftIcon /> : <MenuIcon />}
            </IconButton>
            
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, color: 'text.primary' }}>
              ADE Platform <Chip label={currentProject} size="small" sx={{ ml: 1 }} />
            </Typography>
            
            <ButtonGroup variant="outlined" size="small" sx={{ mr: 2, display: { xs: 'none', md: 'flex' } }}>
              {isGenerating ? (
                <Button 
                  startIcon={<StopIcon />} 
                  color="error"
                  onClick={handleStopGeneration}
                >
                  Stop Build
                </Button>
              ) : (
                <Button 
                  startIcon={<RunIcon />} 
                  color="primary"
                  onClick={() => handleCodeGeneration({})}
                >
                  Build MVP
                </Button>
              )}
              <Button startIcon={<SaveIcon />} onClick={() => handleDesignSave({})}>
                Save
              </Button>
            </ButtonGroup>
            
            <Tooltip title="Toggle chat">
              <IconButton color="inherit" onClick={handleToggleChatPanel} sx={{ color: 'text.primary' }}>
                <Badge color="error" variant="dot" invisible={!chatOpen}>
                  <ChatIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Notifications">
              <IconButton color="inherit" sx={{ ml: 1, color: 'text.primary' }}>
                <Badge badgeContent={notificationsCount} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Switch agent">
              <IconButton 
                onClick={handleMenuOpen}
                sx={{ 
                  ml: 1,
                  color: 'text.primary',
                  bgcolor: 'action.selected',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
              >
                {activeAgent === 'assistant' && <AIIcon />}
                {activeAgent === 'designer' && <DesignIcon />}
                {activeAgent === 'developer' && <CodeIcon />}
                {activeAgent === 'advisor' && <AdvisorIcon />}
              </IconButton>
            </Tooltip>
            
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={() => handleAgentSwitch('assistant')}>
                <ListItemIcon><AIIcon fontSize="small" /></ListItemIcon>
                Assistant Agent
              </MenuItem>
              <MenuItem onClick={() => handleAgentSwitch('designer')}>
                <ListItemIcon><DesignIcon fontSize="small" /></ListItemIcon>
                Designer Agent
              </MenuItem>
              <MenuItem onClick={() => handleAgentSwitch('developer')}>
                <ListItemIcon><CodeIcon fontSize="small" /></ListItemIcon>
                Developer Agent
              </MenuItem>
              <MenuItem onClick={() => handleAgentSwitch('advisor')}>
                <ListItemIcon><AdvisorIcon fontSize="small" /></ListItemIcon>
                Advisor Agent
              </MenuItem>
            </Menu>
            
            <Tooltip title={darkMode ? "Switch to light mode" : "Switch to dark mode"}>
              <IconButton color="inherit" onClick={handleThemeToggle} sx={{ ml: 1, color: 'text.primary' }}>
                {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Tooltip>
          </Toolbar>
          {isGenerating && (
            <TaskProgressBar progress={buildProgress} />
          )}
        </AppBarStyled>
        
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={open}
          onClose={isMobile ? handleDrawerToggle : undefined}
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            whiteSpace: 'nowrap',
            boxSizing: 'border-box',
            ...(open && { ...openedMixin(theme) }),
            ...(!open && { ...closedMixin(theme) }),
            '& .MuiDrawer-paper': {
              ...(open && { ...openedMixin(theme) }),
              ...(!open && { ...closedMixin(theme) }),
            },
          }}
        >
          <DrawerHeader>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              width: '100%', 
              justifyContent: 'space-between',
              p: 1
            }}>
              {open && (
                <Typography variant="h6" color="text.primary" sx={{ fontWeight: 600 }}>
                  ADE Platform
                </Typography>
              )}
            </Box>
          </DrawerHeader>
          <Divider />
          <List>
            {navigation.map((item) => (
              <ListItem 
                button 
                key={item.name}
                component={Link}
                to={item.path}
                sx={{ 
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                  color: 'text.primary'
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                    color: 'text.primary'
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && <ListItemText primary={item.name} />}
              </ListItem>
            ))}
          </List>
          <Divider />
          {open && (
            <Box sx={{ p: 2, mt: 'auto' }}>
              <Typography variant="body2" color="text.secondary" align="center">
                ADE Platform v1.0
              </Typography>
            </Box>
          )}
        </Drawer>
        
        <Main open={open}>
          <DrawerHeader />
          <Box 
            component="div" 
            sx={{ 
              p: { xs: 1, sm: 2, md: 3 },
              display: 'flex',
              flexDirection: 'column',
              height: 'calc(100vh - 64px)'
            }}
          >
            <Grid container spacing={2} sx={{ height: '100%', mb: 2 }}>
              {/* Main content area - takes up all available space minus the right panel */}
              <Grid item xs={12} md={chatOpen ? 8 : 12} sx={{ height: '100%' }}>
                <Paper 
                  elevation={1} 
                  sx={{ 
                    height: '100%', 
                    borderRadius: 2, 
                    overflow: 'hidden', 
                    display: 'flex',
                    flexDirection: 'column'
                  }}
                >
                  <Box sx={{ flex: 1, overflow: 'auto' }}>
                    <Routes>
                      <Route path="/" element={
                        <ErrorBoundary componentName="Home">
                          <Box sx={{ p: 3 }}>
                            <Grid container spacing={3}>
                              <Grid item xs={12}>
                                <ErrorBoundary>
                                  <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                                    <SimpleDiagnostic />
                                    <Box mt={2}>
                                      <DiagnosticPanel />
                                    </Box>
                                    <Box mt={2}>
                                      <PydanticTester />
                                    </Box>
                                  </Box>
                                </ErrorBoundary>
                              </Grid>
                              <Grid item xs={12}>
                                <Typography variant="h5" gutterBottom>Getting Started</Typography>
                                <Typography variant="body1" paragraph>
                                  This is a temporary placeholder for the getting started section.
                                </Typography>
                              </Grid>
                            </Grid>
                          </Box>
                        </ErrorBoundary>
                      } />
                      <Route path="/command-hub/*" element={
                        <ErrorBoundary componentName="CommandHub">
                          <CommandHub 
                            onSave={handleDesignSave} 
                            onGenerateCode={handleCodeGeneration} 
                            isGenerating={isGenerating} 
                            activeAgent={activeAgent} 
                          />
                        </ErrorBoundary>
                      } />
                      <Route path="/settings" element={
                        <ErrorBoundary componentName="Settings">
                          <Settings />
                        </ErrorBoundary>
                      } />
                      <Route path="/test-api" element={
                        <ErrorBoundary componentName="TestApi">
                          <TestApi />
                        </ErrorBoundary>
                      } />
                      <Route path="/prompt-processor" element={
                        <ErrorBoundary componentName="PromptProcessor">
                          <PromptProcessor />
                        </ErrorBoundary>
                      } />
                      <Route path="/error-monitoring" element={
                        <ErrorBoundary componentName="ErrorMonitoringDashboard">
                          <ErrorMonitoringDashboard />
                        </ErrorBoundary>
                      } />
                      <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                  </Box>
                </Paper>
              </Grid>
              
              {/* Right side panel with chat and agent status - only visible when chatOpen is true */}
              {chatOpen && (
                <Grid item xs={12} md={4} sx={{ height: '100%', display: { xs: 'none', md: 'block' } }}>
                  <Grid container spacing={2} sx={{ height: '100%' }}>
                    <Grid item xs={12} sx={{ height: '65%' }}>
                      <Paper 
                        elevation={1} 
                        sx={{ 
                          height: '100%', 
                          borderRadius: 2, 
                          overflow: 'hidden',
                          display: 'flex',
                          flexDirection: 'column'
                        }}
                      >
                        <Box sx={{ 
                          p: 2, 
                          borderBottom: 1, 
                          borderColor: 'divider',
                          display: 'flex',
                          justifyContent: 'space-between'
                        }}>
                          <Typography variant="h6">
                            Agent Communication
                          </Typography>
                          <Tooltip title="Close chat">
                            <IconButton size="small" onClick={handleToggleChatPanel}>
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        <Box sx={{ flex: 1, overflow: 'hidden' }}>
                          <LiveChat activeAgent={activeAgent} />
                        </Box>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sx={{ height: '35%' }}>
                      <Typography variant="h6" gutterBottom>Agent Status</Typography>
                      <Typography variant="body1" paragraph>
                        This is a temporary placeholder for the agent status section.
                      </Typography>
                    </Grid>
                  </Grid>
                </Grid>
              )}
            </Grid>
            
            {/* Status bar at the bottom */}
            <StatusBar>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Tooltip title="System status">
                  <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        mr: 1,
                        backgroundColor: 
                          systemStatus === 'building' ? 'primary.main' :
                          systemStatus === 'completed' ? 'success.main' :
                          systemStatus === 'error' ? 'error.main' :
                          systemStatus === 'stopped' ? 'warning.main' :
                          'text.disabled',
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {systemStatus === 'building' ? 'Building...' :
                       systemStatus === 'completed' ? 'Build completed' :
                       systemStatus === 'error' ? 'Build failed' :
                       systemStatus === 'stopped' ? 'Build stopped' : 'Ready'}
                    </Typography>
                  </Box>
                </Tooltip>
                <Typography variant="caption" color="text.secondary">
                  {isGenerating && `Build progress: ${Math.round(buildProgress)}%`}
                </Typography>
              </Box>
              <Box>
                <Tooltip title="Active agent">
                  <Chip 
                    size="small" 
                    icon={
                      activeAgent === 'assistant' ? <AIIcon fontSize="small" /> :
                      activeAgent === 'designer' ? <DesignIcon fontSize="small" /> :
                      activeAgent === 'developer' ? <CodeIcon fontSize="small" /> :
                      <AdvisorIcon fontSize="small" />
                    } 
                    label={`${activeAgent.charAt(0).toUpperCase() + activeAgent.slice(1)} Agent`}
                    onClick={handleMenuOpen}
                    sx={{ mr: 1 }}
                  />
                </Tooltip>
                <Tooltip title="Current project">
                  <Chip size="small" label={currentProject} variant="outlined" />
                </Tooltip>
              </Box>
            </StatusBar>
          </Box>
        </Main>
        
        {/* Mobile chat toggle button */}
        {!chatOpen && (
          <Fab 
            color="primary" 
            aria-label="open chat"
            onClick={handleToggleChatPanel}
            sx={{ 
              position: 'fixed', 
              bottom: 16, 
              right: 16,
              display: { xs: 'flex', md: 'none' }
            }}
          >
            <ChatIcon />
          </Fab>
        )}
        
        {/* Mobile format chat overlay */}
        {chatOpen && (
          <Box 
            sx={{ 
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              bgcolor: 'background.paper',
              zIndex: 9999,
              display: { xs: 'flex', md: 'none' },
              flexDirection: 'column',
            }}
          >
            <Box sx={{ 
              p: 2, 
              borderBottom: 1, 
              borderColor: 'divider',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <Typography variant="h6">
                Agent Communication
              </Typography>
              <IconButton onClick={handleToggleChatPanel}>
                <CloseIcon />
              </IconButton>
            </Box>
            <Box sx={{ flex: 1, overflow: 'hidden' }}>
              <LiveChat activeAgent={activeAgent} />
            </Box>
          </Box>
        )}
        
        {/* Debug Console Capture - displays errors in the UI */}
        {process.env.NODE_ENV === 'development' && <ConsoleCapture />}
        
        {/* Alert system */}
        <Snackbar
          open={alertOpen}
          autoHideDuration={6000}
          onClose={() => setAlertOpen(false)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={() => setAlertOpen(false)} 
            severity={alertSeverity} 
            variant="filled"
            sx={{ width: '100%' }}
          >
            {alertMessage}
          </Alert>
        </Snackbar>
      </Box>
    </Router>
  );
}

export default App;