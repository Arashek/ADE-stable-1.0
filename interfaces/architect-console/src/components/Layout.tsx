import React from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, useTheme } from '@mui/material';
import {
  Menu as MenuIcon,
  Refresh as RefreshIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useAppContext } from '../context/AppContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const { isOnline, lastUpdate, error, clearError } = useAppContext();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Architect's Blueprint Console
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit" aria-label="refresh">
              <RefreshIcon />
            </IconButton>
            <IconButton color="inherit" aria-label="notifications">
              <NotificationsIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          bgcolor: theme.palette.background.default,
        }}
      >
        {error && (
          <Box
            sx={{
              p: 2,
              bgcolor: theme.palette.error.main,
              color: theme.palette.error.contrastText,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography>{error}</Typography>
            <IconButton
              size="small"
              color="inherit"
              onClick={clearError}
              sx={{ ml: 2 }}
            >
              <RefreshIcon />
            </IconButton>
          </Box>
        )}

        {!isOnline && (
          <Box
            sx={{
              p: 2,
              bgcolor: theme.palette.warning.main,
              color: theme.palette.warning.contrastText,
            }}
          >
            <Typography>You are currently offline</Typography>
          </Box>
        )}

        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {children}
        </Box>

        {lastUpdate && (
          <Box
            sx={{
              p: 1,
              textAlign: 'center',
              bgcolor: theme.palette.background.paper,
              borderTop: 1,
              borderColor: 'divider',
            }}
          >
            <Typography variant="caption" color="text.secondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default Layout; 