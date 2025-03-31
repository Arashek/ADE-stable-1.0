import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  IconButton,
  Typography,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Close as CloseIcon,
  SwapHoriz as SwapHorizIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { useGlobal } from '../state/GlobalContext';
import MediaProcessor from './MediaProcessor';
import PerformanceMonitor from './PerformanceMonitor';

const CommandCenter = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { state, dispatch } = useGlobal();
  const [position, setPosition] = useState('right');
  const [activeTab, setActiveTab] = useState('media');
  const commandCenterRef = useRef(null);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.ctrlKey && event.key === 'k') {
        event.preventDefault();
        dispatch({ type: 'TOGGLE_COMMAND_CENTER' });
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [dispatch]);

  // Auto-open on errors
  useEffect(() => {
    if (state.errors?.length > 0) {
      dispatch({ type: 'TOGGLE_COMMAND_CENTER', payload: true });
    }
  }, [state.errors, dispatch]);

  const togglePosition = () => {
    setPosition(position === 'right' ? 'left' : 'right');
  };

  const handleClose = () => {
    dispatch({ type: 'TOGGLE_COMMAND_CENTER', payload: false });
  };

  if (!state.isCommandCenterOpen) {
    return (
      <IconButton
        onClick={() => dispatch({ type: 'TOGGLE_COMMAND_CENTER', payload: true })}
        sx={{
          position: 'fixed',
          [position]: 16,
          top: 16,
          zIndex: 1200,
          backgroundColor: 'background.paper',
          boxShadow: 2
        }}
      >
        <SpeedIcon />
      </IconButton>
    );
  }

  return (
    <Paper
      ref={commandCenterRef}
      elevation={3}
      sx={{
        position: 'fixed',
        [position]: 0,
        top: 0,
        bottom: 0,
        width: isMobile ? '100%' : 400,
        zIndex: 1200,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Command Center
        </Typography>
        <IconButton onClick={togglePosition} size="small">
          <SwapHorizIcon />
        </IconButton>
        <IconButton onClick={handleClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      <Box sx={{ display: 'flex', borderBottom: 1, borderColor: 'divider' }}>
        <Box
          sx={{
            flex: 1,
            p: 1,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: activeTab === 'media' ? 'action.selected' : 'transparent'
          }}
          onClick={() => setActiveTab('media')}
        >
          <Typography variant="body2">Media</Typography>
        </Box>
        <Box
          sx={{
            flex: 1,
            p: 1,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: activeTab === 'performance' ? 'action.selected' : 'transparent'
          }}
          onClick={() => setActiveTab('performance')}
        >
          <Typography variant="body2">Performance</Typography>
        </Box>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {activeTab === 'media' ? (
          <MediaProcessor />
        ) : (
          <PerformanceMonitor />
        )}
      </Box>
    </Paper>
  );
};

export default CommandCenter; 