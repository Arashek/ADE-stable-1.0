import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

// Define error log interface
interface ErrorLog {
  id: string;
  timestamp: string;
  category: string;
  severity: string;
  message: string;
  component?: string;
  source?: string;
  context?: any;
  traceback?: string;
}

// API service for error logs
const errorLogsApi = {
  getErrorLogs: async (
    limit: number = 100,
    page: number = 0,
    category?: string,
    severity?: string,
    component?: string
  ): Promise<{ logs: ErrorLog[], total: number }> => {
    try {
      // Build the API URL with query parameters
      let url = `http://localhost:8000/error-logging/recent?limit=${limit}`;
      
      if (category) {
        url += `&category=${category}`;
      }
      if (severity) {
        url += `&severity=${severity}`;
      }
      if (component) {
        url += `&component=${component}`;
      }
      
      // Fetch errors from the backend API
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Error fetching logs: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Transform the data to match our ErrorLog interface
      const logs: ErrorLog[] = data.errors.map((error: any) => ({
        id: error.error_id,
        timestamp: error.timestamp,
        category: error.category,
        severity: error.severity,
        message: error.message,
        component: error.component,
        source: error.source,
        context: error.context,
        traceback: error.stack_trace || error.traceback
      }));
      
      return { logs, total: data.total };
    } catch (error) {
      console.error('Error fetching error logs:', error);
      
      // Fallback to localStorage if the API call fails
      const storedLogs = localStorage.getItem('ade_error_logs');
      if (storedLogs) {
        let logs: ErrorLog[] = JSON.parse(storedLogs);
        
        // Apply filters
        if (category) {
          logs = logs.filter(log => log.category === category);
        }
        if (severity) {
          logs = logs.filter(log => log.severity === severity);
        }
        if (component) {
          logs = logs.filter(log => log.component === component);
        }
        
        // Sort by timestamp (newest first)
        logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        
        // Paginate
        const paginatedLogs = logs.slice(page * limit, (page + 1) * limit);
        
        return { logs: paginatedLogs, total: logs.length };
      }
      
      return { logs: [], total: 0 };
    }
  },
  
  clearErrorLogs: async (): Promise<boolean> => {
    try {
      // Call the backend API to clear error logs
      // Note: This endpoint doesn't exist yet in the backend
      const response = await fetch('http://localhost:8000/error-logging/clear', {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Error clearing logs: ${response.statusText}`);
      }
      
      return true;
    } catch (error) {
      console.error('Error clearing error logs:', error);
      
      // Fallback to localStorage if the API call fails
      localStorage.setItem('ade_error_logs', JSON.stringify([]));
      return false;
    }
  },
  
  // For demo purposes, load the test data
  loadTestData: async (): Promise<boolean> => {
    try {
      // Generate some test data
      const categories = ['AGENT', 'API', 'FRONTEND', 'SYSTEM', 'COORDINATION'];
      const severities = ['CRITICAL', 'ERROR', 'WARNING', 'INFO'];
      const components = ['backend', 'frontend', 'agent', 'coordination'];
      const sources = [
        'backend.main',
        'backend.agents.agent_coordinator',
        'frontend.src.components.ErrorBoundary',
        'frontend.src.services.api'
      ];
      const errorMessages = [
        'Connection refused',
        'Failed to initialize agent',
        'Invalid response format',
        'Timeout waiting for agent response',
        'Authentication failed',
        'Resource not found',
        'Invalid input format',
        'Database connection error'
      ];
      
      const testLogs: ErrorLog[] = [];
      
      for (let i = 0; i < 50; i++) {
        const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString();
        const category = categories[Math.floor(Math.random() * categories.length)];
        const severity = severities[Math.floor(Math.random() * severities.length)];
        const component = components[Math.floor(Math.random() * components.length)];
        const source = sources[Math.floor(Math.random() * sources.length)];
        const errorMessage = errorMessages[Math.floor(Math.random() * errorMessages.length)];
        
        testLogs.push({
          id: `test-${i}-${Date.now()}`,
          timestamp,
          category,
          severity,
          message: errorMessage,
          component,
          source,
          context: {
            test: true,
            index: i,
            random_value: Math.floor(Math.random() * 1000)
          },
          traceback: severity === 'CRITICAL' || severity === 'ERROR' 
            ? `Traceback (most recent call last):\n  File "${source}.py", line ${Math.floor(Math.random() * 100) + 1}, in <module>\n    raise Exception("${errorMessage}")\nException: ${errorMessage}`
            : undefined
        });
      }
      
      localStorage.setItem('ade_error_logs', JSON.stringify(testLogs));
      return true;
    } catch (error) {
      console.error('Error loading test data:', error);
      return false;
    }
  }
};

// Severity chip component
const SeverityChip: React.FC<{ severity: string }> = ({ severity }) => {
  let color: 'error' | 'warning' | 'info' | 'success' = 'info';
  let icon = <InfoIcon />;
  
  switch (severity) {
    case 'CRITICAL':
      color = 'error';
      icon = <ErrorIcon />;
      break;
    case 'ERROR':
      color = 'error';
      icon = <ErrorIcon />;
      break;
    case 'WARNING':
      color = 'warning';
      icon = <WarningIcon />;
      break;
    case 'INFO':
      color = 'info';
      icon = <InfoIcon />;
      break;
    default:
      color = 'info';
      icon = <InfoIcon />;
  }
  
  return (
    <Chip
      icon={icon}
      label={severity}
      color={color}
      size="small"
      variant="outlined"
    />
  );
};

// Error Logs Panel component
const ErrorLogsPanel: React.FC = () => {
  // State
  const [logs, setLogs] = useState<ErrorLog[]>([]);
  const [totalLogs, setTotalLogs] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [selectedLog, setSelectedLog] = useState<ErrorLog | null>(null);
  const [filterDialogOpen, setFilterDialogOpen] = useState<boolean>(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [componentFilter, setComponentFilter] = useState<string>('');
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info' | 'warning'>('info');
  
  // Stats
  const [stats, setStats] = useState<{
    critical: number;
    error: number;
    warning: number;
    info: number;
    total: number;
  }>({
    critical: 0,
    error: 0,
    warning: 0,
    info: 0,
    total: 0
  });
  
  // Load logs
  const loadLogs = async () => {
    setLoading(true);
    try {
      const result = await errorLogsApi.getErrorLogs(
        rowsPerPage,
        page,
        categoryFilter || undefined,
        severityFilter || undefined,
        componentFilter || undefined
      );
      
      setLogs(result.logs);
      setTotalLogs(result.total);
      
      // Calculate stats
      const allLogs = await errorLogsApi.getErrorLogs(1000); // Get all logs for stats
      const critical = allLogs.logs.filter(log => log.severity === 'CRITICAL').length;
      const error = allLogs.logs.filter(log => log.severity === 'ERROR').length;
      const warning = allLogs.logs.filter(log => log.severity === 'WARNING').length;
      const info = allLogs.logs.filter(log => log.severity === 'INFO').length;
      
      setStats({
        critical,
        error,
        warning,
        info,
        total: allLogs.total
      });
    } catch (error) {
      console.error('Error loading logs:', error);
      showSnackbar('Failed to load error logs', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // Load logs on mount and when filters/pagination change
  useEffect(() => {
    loadLogs();
  }, [page, rowsPerPage, categoryFilter, severityFilter, componentFilter]);
  
  // Handle page change
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };
  
  // Handle rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Handle log selection
  const handleLogSelect = (log: ErrorLog) => {
    setSelectedLog(log);
  };
  
  // Handle log dialog close
  const handleLogDialogClose = () => {
    setSelectedLog(null);
  };
  
  // Handle filter dialog open
  const handleFilterDialogOpen = () => {
    setFilterDialogOpen(true);
  };
  
  // Handle filter dialog close
  const handleFilterDialogClose = () => {
    setFilterDialogOpen(false);
  };
  
  // Handle filter apply
  const handleFilterApply = () => {
    setPage(0);
    setFilterDialogOpen(false);
    loadLogs();
  };
  
  // Handle filter reset
  const handleFilterReset = () => {
    setCategoryFilter('');
    setSeverityFilter('');
    setComponentFilter('');
    setPage(0);
    setFilterDialogOpen(false);
    loadLogs();
  };
  
  // Handle clear logs
  const handleClearLogs = async () => {
    if (window.confirm('Are you sure you want to clear all error logs? This action cannot be undone.')) {
      setLoading(true);
      try {
        const success = await errorLogsApi.clearErrorLogs();
        if (success) {
          showSnackbar('Error logs cleared successfully', 'success');
          loadLogs();
        } else {
          showSnackbar('Failed to clear error logs', 'error');
        }
      } catch (error) {
        console.error('Error clearing logs:', error);
        showSnackbar('Failed to clear error logs', 'error');
      } finally {
        setLoading(false);
      }
    }
  };
  
  // Handle load test data
  const handleLoadTestData = async () => {
    setLoading(true);
    try {
      const success = await errorLogsApi.loadTestData();
      if (success) {
        showSnackbar('Test data loaded successfully', 'success');
        loadLogs();
      } else {
        showSnackbar('Failed to load test data', 'error');
      }
    } catch (error) {
      console.error('Error loading test data:', error);
      showSnackbar('Failed to load test data', 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // Show snackbar
  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };
  
  // Handle snackbar close
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Error Logs
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical Errors
              </Typography>
              <Typography variant="h3" component="div" color="error">
                {stats.critical}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Errors
              </Typography>
              <Typography variant="h3" component="div" color="error">
                {stats.error}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Warnings
              </Typography>
              <Typography variant="h3" component="div" color="warning.main">
                {stats.warning}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Info Messages
              </Typography>
              <Typography variant="h3" component="div" color="info.main">
                {stats.info}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Action Buttons */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadLogs}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={handleFilterDialogOpen}
            sx={{ mr: 1 }}
          >
            Filter
          </Button>
        </Box>
        <Box>
          <Button
            variant="outlined"
            onClick={handleLoadTestData}
            sx={{ mr: 1 }}
          >
            Load Test Data
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleClearLogs}
          >
            Clear Logs
          </Button>
        </Box>
      </Box>
      
      {/* Applied Filters */}
      {(categoryFilter || severityFilter || componentFilter) && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Applied Filters:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {categoryFilter && (
              <Chip
                label={`Category: ${categoryFilter}`}
                onDelete={() => setCategoryFilter('')}
                size="small"
              />
            )}
            {severityFilter && (
              <Chip
                label={`Severity: ${severityFilter}`}
                onDelete={() => setSeverityFilter('')}
                size="small"
              />
            )}
            {componentFilter && (
              <Chip
                label={`Component: ${componentFilter}`}
                onDelete={() => setComponentFilter('')}
                size="small"
              />
            )}
            <Button
              size="small"
              onClick={handleFilterReset}
            >
              Reset All
            </Button>
          </Box>
        </Box>
      )}
      
      {/* Error Logs Table */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Component</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress size={24} sx={{ my: 2 }} />
                  </TableCell>
                </TableRow>
              ) : logs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" sx={{ py: 2 }}>
                      No error logs found.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                logs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>{formatDate(log.timestamp)}</TableCell>
                    <TableCell>
                      <SeverityChip severity={log.severity} />
                    </TableCell>
                    <TableCell>{log.category}</TableCell>
                    <TableCell>{log.component}</TableCell>
                    <TableCell>
                      {log.message.length > 50
                        ? `${log.message.substring(0, 50)}...`
                        : log.message}
                    </TableCell>
                    <TableCell>{log.source || 'N/A'}</TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleLogSelect(log)}
                        >
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalLogs}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      
      {/* Error Log Details Dialog */}
      <Dialog
        open={selectedLog !== null}
        onClose={handleLogDialogClose}
        maxWidth="md"
        fullWidth
      >
        {selectedLog && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">
                  Error Log Details
                </Typography>
                <IconButton
                  edge="end"
                  color="inherit"
                  onClick={handleLogDialogClose}
                  aria-label="close"
                >
                  <CloseIcon />
                </IconButton>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">ID:</Typography>
                  <Typography variant="body2" gutterBottom>{selectedLog.id}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Timestamp:</Typography>
                  <Typography variant="body2" gutterBottom>{formatDate(selectedLog.timestamp)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Severity:</Typography>
                  <Box sx={{ mt: 0.5, mb: 1 }}>
                    <SeverityChip severity={selectedLog.severity} />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Category:</Typography>
                  <Typography variant="body2" gutterBottom>{selectedLog.category}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Component:</Typography>
                  <Typography variant="body2" gutterBottom>{selectedLog.component}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Source:</Typography>
                  <Typography variant="body2" gutterBottom>{selectedLog.source || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2">Error Message:</Typography>
                  <Paper variant="outlined" sx={{ p: 1, mt: 0.5, mb: 2, backgroundColor: '#f5f5f5' }}>
                    <Typography variant="body2">{selectedLog.message}</Typography>
                  </Paper>
                </Grid>
                {selectedLog.traceback && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2">Traceback:</Typography>
                    <Box sx={{ mt: 0.5, mb: 2 }}>
                      <SyntaxHighlighter language="python" style={docco} customStyle={{ fontSize: '0.8rem' }}>
                        {selectedLog.traceback}
                      </SyntaxHighlighter>
                    </Box>
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Typography variant="subtitle2">Context:</Typography>
                  <Box sx={{ mt: 0.5, mb: 2 }}>
                    <SyntaxHighlighter language="json" style={docco} customStyle={{ fontSize: '0.8rem' }}>
                      {JSON.stringify(selectedLog.context, null, 2)}
                    </SyntaxHighlighter>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleLogDialogClose}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
      
      {/* Filter Dialog */}
      <Dialog
        open={filterDialogOpen}
        onClose={handleFilterDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Filter Error Logs</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="category-filter-label">Category</InputLabel>
              <Select
                labelId="category-filter-label"
                value={categoryFilter}
                label="Category"
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="AGENT">AGENT</MenuItem>
                <MenuItem value="API">API</MenuItem>
                <MenuItem value="AUTH">AUTH</MenuItem>
                <MenuItem value="DATABASE">DATABASE</MenuItem>
                <MenuItem value="FRONTEND">FRONTEND</MenuItem>
                <MenuItem value="IMPORT">IMPORT</MenuItem>
                <MenuItem value="SYSTEM">SYSTEM</MenuItem>
                <MenuItem value="COORDINATION">COORDINATION</MenuItem>
                <MenuItem value="UNKNOWN">UNKNOWN</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="severity-filter-label">Severity</InputLabel>
              <Select
                labelId="severity-filter-label"
                value={severityFilter}
                label="Severity"
                onChange={(e) => setSeverityFilter(e.target.value)}
              >
                <MenuItem value="">All Severities</MenuItem>
                <MenuItem value="CRITICAL">CRITICAL</MenuItem>
                <MenuItem value="ERROR">ERROR</MenuItem>
                <MenuItem value="WARNING">WARNING</MenuItem>
                <MenuItem value="INFO">INFO</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="component-filter-label">Component</InputLabel>
              <Select
                labelId="component-filter-label"
                value={componentFilter}
                label="Component"
                onChange={(e) => setComponentFilter(e.target.value)}
              >
                <MenuItem value="">All Components</MenuItem>
                <MenuItem value="backend">Backend</MenuItem>
                <MenuItem value="frontend">Frontend</MenuItem>
                <MenuItem value="agent">Agent</MenuItem>
                <MenuItem value="coordination">Coordination</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleFilterReset}>Reset</Button>
          <Button onClick={handleFilterDialogClose}>Cancel</Button>
          <Button onClick={handleFilterApply} variant="contained">Apply</Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ErrorLogsPanel;
