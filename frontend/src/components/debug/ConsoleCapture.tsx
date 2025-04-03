import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  Divider
} from '@mui/material';
import { ExpandMore, BugReport, Close, Delete } from '@mui/icons-material';

// Interface for console log entry
interface ConsoleLogEntry {
  type: 'log' | 'info' | 'warn' | 'error';
  message: string;
  timestamp: Date;
  details?: any;
}

/**
 * ConsoleCapture component - captures console logs and displays them in the UI for debugging
 */
const ConsoleCapture: React.FC = () => {
  const [logs, setLogs] = useState<ConsoleLogEntry[]>([]);
  const [expanded, setExpanded] = useState<boolean>(true);
  const [errorCount, setErrorCount] = useState<number>(0);
  const [warningCount, setWarningCount] = useState<number>(0);

  // Capture console logs
  useEffect(() => {
    // Save original console methods
    const originalConsole = {
      log: console.log,
      info: console.info,
      warn: console.warn,
      error: console.error
    };

    // Function to add log to state
    const addLog = (type: 'log' | 'info' | 'warn' | 'error', args: any[]) => {
      // Create log entry
      const message = args.map(arg => {
        if (typeof arg === 'object') {
          try {
            return JSON.stringify(arg);
          } catch (e) {
            return String(arg);
          }
        }
        return String(arg);
      }).join(' ');

      // Update logs state
      setLogs(prevLogs => {
        const newLog: ConsoleLogEntry = {
          type,
          message,
          timestamp: new Date(),
          details: args.length > 0 ? args[0] : undefined
        };
        
        // Only keep latest 100 logs
        const updatedLogs = [newLog, ...prevLogs].slice(0, 100);
        
        // Update counts
        if (type === 'error') {
          setErrorCount(prevCount => prevCount + 1);
        } else if (type === 'warn') {
          setWarningCount(prevCount => prevCount + 1);
        }
        
        return updatedLogs;
      });
    };

    // Override console methods
    console.log = (...args) => {
      originalConsole.log(...args);
      addLog('log', args);
    };

    console.info = (...args) => {
      originalConsole.info(...args);
      addLog('info', args);
    };

    console.warn = (...args) => {
      originalConsole.warn(...args);
      addLog('warn', args);
    };

    console.error = (...args) => {
      originalConsole.error(...args);
      addLog('error', args);
    };

    // Cleanup function to restore original console
    return () => {
      console.log = originalConsole.log;
      console.info = originalConsole.info;
      console.warn = originalConsole.warn;
      console.error = originalConsole.error;
    };
  }, []);

  // Handle clear logs
  const handleClearLogs = () => {
    setLogs([]);
    setErrorCount(0);
    setWarningCount(0);
  };

  // Get color for log type
  const getLogColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'error.main';
      case 'warn':
        return 'warning.main';
      case 'info':
        return 'info.main';
      default:
        return 'text.primary';
    }
  };

  // Format timestamp
  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString();
  };

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        width: expanded ? 600 : 'auto',
        maxWidth: '90vw',
        zIndex: 9999,
        opacity: 0.95,
        transition: 'all 0.3s ease'
      }}
    >
      <Accordion
        expanded={expanded}
        onChange={() => setExpanded(!expanded)}
        sx={{ boxShadow: 'none' }}
      >
        <AccordionSummary
          expandIcon={<ExpandMore />}
          sx={{ 
            bgcolor: errorCount > 0 ? 'error.light' : warningCount > 0 ? 'warning.light' : 'info.light',
            borderTopLeftRadius: 4,
            borderTopRightRadius: 4
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <BugReport sx={{ mr: 1 }} />
              <Typography variant="subtitle1">
                Console Capture
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {errorCount > 0 && (
                <Chip 
                  label={`${errorCount} Errors`} 
                  color="error" 
                  size="small" 
                />
              )}
              {warningCount > 0 && (
                <Chip 
                  label={`${warningCount} Warnings`} 
                  color="warning" 
                  size="small" 
                />
              )}
              <Button
                size="small"
                startIcon={<Delete />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleClearLogs();
                }}
              >
                Clear
              </Button>
            </Box>
          </Box>
        </AccordionSummary>

        <AccordionDetails sx={{ p: 0, maxHeight: '400px', overflow: 'auto' }}>
          {logs.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No console logs captured yet.
              </Typography>
            </Box>
          ) : (
            <Box>
              {logs.map((log, index) => (
                <Box key={index} sx={{ p: 2, bgcolor: index % 2 === 0 ? 'background.default' : 'background.paper' }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography
                      variant="caption"
                      component="span"
                      sx={{ color: getLogColor(log.type), fontWeight: 'bold', textTransform: 'uppercase' }}
                    >
                      {log.type}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(log.timestamp)}
                    </Typography>
                  </Box>
                  <Typography
                    variant="body2"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      fontFamily: 'monospace',
                      color: getLogColor(log.type)
                    }}
                  >
                    {log.message}
                  </Typography>
                  {index < logs.length - 1 && <Divider sx={{ mt: 1 }} />}
                </Box>
              ))}
            </Box>
          )}
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default ConsoleCapture;
