import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import { Box, Grid } from '@mui/material';
import CommandPanel from './components/CommandPanel';
import ProjectTimeline from './components/ProjectTimeline';
import CodeEvolution from './components/CodeEvolution';
import AgentCommunication from './components/AgentCommunication';
import RuntimePreview from './components/RuntimePreview';
import ChatPanel from './components/ChatPanel';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Fira Code", "Roboto Mono", monospace',
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#121212',
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Grid container spacing={2} sx={{ flex: 1, p: 2 }}>
          {/* Main Content Area */}
          <Grid item xs={12} md={8} sx={{ display: 'flex', flexDirection: 'column' }}>
            <CommandPanel />
            <ProjectTimeline />
            <CodeEvolution />
            <AgentCommunication />
            <RuntimePreview />
          </Grid>
          
          {/* Chat Panel */}
          <Grid item xs={12} md={4}>
            <ChatPanel />
          </Grid>
        </Grid>
      </Box>
    </ThemeProvider>
  );
};

export default App; 