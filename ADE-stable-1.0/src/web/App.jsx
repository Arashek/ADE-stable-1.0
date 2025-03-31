import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { GlobalProvider } from './state/GlobalContext';
import MediaProcessingPage from './pages/MediaProcessingPage';
import CommandCenter from './components/CommandCenter';
import NotificationSystem from './components/NotificationSystem';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <GlobalProvider>
        <Router>
          <div style={{ display: 'flex', height: '100vh' }}>
            {/* Main Content */}
            <main style={{ flex: 1, overflow: 'auto' }}>
              <Routes>
                <Route path="/media" element={<MediaProcessingPage />} />
                {/* Add other routes here */}
              </Routes>
            </main>

            {/* Command Center */}
            <CommandCenter />

            {/* Notification System */}
            <NotificationSystem />
          </div>
        </Router>
      </GlobalProvider>
    </ThemeProvider>
  );
};

export default App; 