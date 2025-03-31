import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
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
  ThemeProvider,
  CssBaseline,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Code as CodeIcon,
  Palette as DesignIcon,
  Psychology as AIIcon,
  Build as ToolsIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { theme } from './theme';
import CommandHub from './components/CommandHub';
import LiveChat from './components/LiveChat';
import { LoadingStates } from './components/common/LoadingStates';
import { GestureControls } from './components/common/GestureControls';
import { TransitionWrapper } from './components/common/TransitionWrapper';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './routes/Home';
import ModelDashboard from './components/ModelDashboard';
import Analytics from './routes/Analytics';
import Settings from './routes/Settings';
import CodeAnalyzer from './components/CodeAnalyzer';
import AgentCoordinator from './components/AgentCoordinator';
import SpecializedAgents from './components/agents/SpecializedAgents';
import CoordinationHub from './components/agents/CoordinationHub';
import PerformanceMonitor from './components/PerformanceMonitor';
import { AgentDashboard } from './components/agents/AgentDashboard';
import { CoordinationSystem } from './components/agents/CoordinationSystem';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { MainDashboard } from './components/MainDashboard';
import { DocumentationPanel } from './components/DocumentationPanel';
import { useAuth } from './hooks/useAuth';

const drawerWidth = 240;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
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
    marginLeft: drawerWidth,
  }),
}));

const AppBarStyled = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<{
  open?: boolean;
}>(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: drawerWidth,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  const [open, setOpen] = useState(true);
  const [activeAgent, setActiveAgent] = useState<string>('design');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleDesignSave = async (design: any) => {
    try {
      const response = await fetch('/api/designs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(design),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save design');
      }
      
      console.log('Design saved successfully');
    } catch (error) {
      console.error('Error saving design:', error);
    }
  };

  const handleCodeGeneration = async (design: any) => {
    try {
      setIsGenerating(true);
      const response = await fetch('/api/generate-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(design),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate code');
      }
      
      const generatedCode = await response.json();
      console.log('Code generated:', generatedCode);
    } catch (error) {
      console.error('Error generating code:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    try {
      setIsGenerating(true);
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, agent: activeAgent }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      const reader = response.body?.getReader();
      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        console.log('Received chunk:', text);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStopGeneration = async () => {
    try {
      const response = await fetch('/api/stop-generation', {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to stop generation');
      }
      
      setIsGenerating(false);
    } catch (error) {
      console.error('Error stopping generation:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Box sx={{ display: 'flex', bgcolor: 'grey.900', minHeight: '100vh' }}>
          <AppBarStyled position="fixed" open={open}>
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={handleDrawerToggle}
                edge="start"
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div">
                ADE Platform
              </Typography>
            </Toolbar>
          </AppBarStyled>

          <Drawer
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
                bgcolor: 'grey.900',
                color: 'white',
              },
            }}
            variant="persistent"
            anchor="left"
            open={open}
          >
            <DrawerHeader />
            <List>
              <ListItem button>
                <ListItemIcon>
                  <CodeIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText primary="Code" />
              </ListItem>
              <ListItem button>
                <ListItemIcon>
                  <DesignIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText primary="Design" />
              </ListItem>
              <ListItem button>
                <ListItemIcon>
                  <AIIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText primary="AI" />
              </ListItem>
              <ListItem button>
                <ListItemIcon>
                  <ToolsIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText primary="Tools" />
              </ListItem>
            </List>
          </Drawer>

          <Main open={open}>
            <DrawerHeader />
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route
                  path="/projects/:projectId/metrics"
                  element={
                    <PrivateRoute>
                      <ProjectMetrics />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/sprints/:sprintId"
                  element={
                    <PrivateRoute>
                      <SprintBoard />
                    </PrivateRoute>
                  }
                />
              </Routes>
            </Container>
          </Main>

          <DocumentationPanel />
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App; 