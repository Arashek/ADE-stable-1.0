import React from 'react';
import { 
  Box, 
  Typography, 
  AppBar, 
  Toolbar, 
  Container, 
  Paper, 
  ThemeProvider,
  CssBaseline,
  createTheme,
} from '@mui/material';

/**
 * Minimal App Component
 * 
 * This is a simplified version of the main application that removes complex components
 * that might be causing TypeScript errors. Once this is running correctly, we can
 * incrementally add back the original components.
 */
const MinimalApp: React.FC = () => {
  // Create a basic theme
  const theme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#3f51b5',
      },
      secondary: {
        main: '#f50057',
      },
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              ADE Platform (Simplified)
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
          <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
            <Typography variant="h5" component="h2" gutterBottom>
              ADE Platform Frontend
            </Typography>
            <Typography>
              This is a simplified version of the ADE Platform frontend that verifies
              the basic environment is running correctly.
            </Typography>
          </Paper>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 3 }}>
            <Paper sx={{ p: 3, height: '200px' }}>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                height: '70%',
                bgcolor: 'success.dark',
                color: 'white',
                borderRadius: 1
              }}>
                <Typography variant="h5">OPERATIONAL</Typography>
              </Box>
            </Paper>
            
            <Paper sx={{ p: 3, height: '200px' }}>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                gap: 1
              }}>
                {['Validator', 'Designer', 'Architect', 'Security', 'Performance'].map(agent => (
                  <Box 
                    key={agent}
                    sx={{ 
                      p: 1, 
                      bgcolor: 'primary.dark',
                      color: 'white',
                      borderRadius: 1,
                      display: 'flex',
                      justifyContent: 'space-between'
                    }}
                  >
                    <Typography>{agent}</Typography>
                    <Typography>Ready</Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Box>
        </Container>
        
        <Box component="footer" sx={{ bgcolor: 'background.paper', p: 2, mt: 'auto' }}>
          <Typography variant="body2" color="text.secondary" align="center">
            ADE Platform - {new Date().getFullYear()}
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default MinimalApp;
