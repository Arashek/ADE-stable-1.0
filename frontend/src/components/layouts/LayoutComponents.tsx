import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { LayoutType } from '../LayoutToggle';

interface LayoutComponentsProps {
  layout: LayoutType;
  children: React.ReactNode;
}

// Grid Matrix Layout
const GridMatrixLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Grid container spacing={2} sx={{ height: '100vh', p: 2 }}>
      <Grid item xs={12} md={6}>
        <Paper sx={{ height: '100%', p: 2 }}>
          <Typography variant="h6" gutterBottom>Command Center</Typography>
          {/* Command Center Content */}
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper sx={{ height: '100%', p: 2 }}>
          <Typography variant="h6" gutterBottom>Preview Window</Typography>
          {/* Preview Window Content */}
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper sx={{ height: '100%', p: 2 }}>
          <Typography variant="h6" gutterBottom>WebIDE</Typography>
          {children}
        </Paper>
      </Grid>
      <Grid item xs={12} md={6}>
        <Paper sx={{ height: '100%', p: 2 }}>
          <Typography variant="h6" gutterBottom>Agent Activities</Typography>
          {/* Agent Activities Content */}
        </Paper>
      </Grid>
    </Grid>
  );
};

// Command First Layout
const CommandFirstLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6">Command Center</Typography>
        {/* Command Center Content */}
      </Paper>
      <Box sx={{ flexGrow: 1, display: 'flex', gap: 2 }}>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>WebIDE</Typography>
          {children}
        </Paper>
        <Box sx={{ width: '300px', display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="h6" gutterBottom>Preview Window</Typography>
            {/* Preview Window Content */}
          </Paper>
          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="h6" gutterBottom>Agent Activities</Typography>
            {/* Agent Activities Content */}
          </Paper>
        </Box>
      </Box>
    </Box>
  );
};

// Agent Centric Layout
const AgentCentricLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box sx={{ height: '100vh', display: 'flex' }}>
      <Paper sx={{ width: '300px', p: 2 }}>
        <Typography variant="h6" gutterBottom>Command Center</Typography>
        {/* Command Center Content */}
      </Paper>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2 }}>
        <Paper sx={{ flex: 1, p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>Agent Activities</Typography>
          {/* Agent Activities Content */}
        </Paper>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>WebIDE</Typography>
          {children}
        </Paper>
      </Box>
      <Paper sx={{ width: '300px', p: 2 }}>
        <Typography variant="h6" gutterBottom>Preview Window</Typography>
        {/* Preview Window Content */}
      </Paper>
    </Box>
  );
};

// Preview Focused Layout
const PreviewFocusedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6">Command Center</Typography>
        {/* Command Center Content */}
      </Paper>
      <Box sx={{ flexGrow: 1, display: 'flex', gap: 2 }}>
        <Paper sx={{ width: '300px', p: 2 }}>
          <Typography variant="h6" gutterBottom>WebIDE</Typography>
          {children}
        </Paper>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>Preview Window</Typography>
          {/* Preview Window Content */}
        </Paper>
        <Paper sx={{ width: '300px', p: 2 }}>
          <Typography variant="h6" gutterBottom>Agent Activities</Typography>
          {/* Agent Activities Content */}
        </Paper>
      </Box>
    </Box>
  );
};

// Chat Driven Layout
const ChatDrivenLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box sx={{ height: '100vh', display: 'flex' }}>
      <Paper sx={{ width: '300px', p: 2 }}>
        <Typography variant="h6" gutterBottom>Command Center</Typography>
        {/* Command Center Content */}
      </Paper>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2 }}>
        <Paper sx={{ flex: 1, p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>Chat Stream</Typography>
          {/* Chat Stream Content */}
        </Paper>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>WebIDE</Typography>
          {children}
        </Paper>
      </Box>
      <Box sx={{ width: '300px', display: 'flex', flexDirection: 'column', gap: 2, p: 2 }}>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>Preview Window</Typography>
          {/* Preview Window Content */}
        </Paper>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>Agent Activities</Typography>
          {/* Agent Activities Content */}
        </Paper>
      </Box>
    </Box>
  );
};

// Dynamic Flow Layout
const DynamicFlowLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Grid container spacing={2} sx={{ height: '100vh', p: 2 }}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6">Command Center</Typography>
          {/* Command Center Content */}
        </Paper>
      </Grid>
      <Grid item xs={12} md={8}>
        <Paper sx={{ height: '100%', p: 2 }}>
          <Typography variant="h6" gutterBottom>WebIDE</Typography>
          {children}
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="h6" gutterBottom>Preview Window</Typography>
            {/* Preview Window Content */}
          </Paper>
          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="h6" gutterBottom>Agent Activities</Typography>
            {/* Agent Activities Content */}
          </Paper>
        </Box>
      </Grid>
    </Grid>
  );
};

export const LayoutComponents: React.FC<LayoutComponentsProps> = ({
  layout,
  children,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const renderLayout = () => {
    switch (layout) {
      case 'grid-matrix':
        return <GridMatrixLayout>{children}</GridMatrixLayout>;
      case 'command-first':
        return <CommandFirstLayout>{children}</CommandFirstLayout>;
      case 'agent-centric':
        return <AgentCentricLayout>{children}</AgentCentricLayout>;
      case 'preview-focused':
        return <PreviewFocusedLayout>{children}</PreviewFocusedLayout>;
      case 'chat-driven':
        return <ChatDrivenLayout>{children}</ChatDrivenLayout>;
      case 'dynamic-flow':
        return <DynamicFlowLayout>{children}</DynamicFlowLayout>;
      default:
        return <GridMatrixLayout>{children}</GridMatrixLayout>;
    }
  };

  return renderLayout();
};
