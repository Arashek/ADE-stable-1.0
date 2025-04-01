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
  Divider,
  Stack,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material';
import { api } from '../../services/api';
import { ErrorCategory, ErrorSeverity } from '../../services/error-logging.service';

// Types for error data
interface ErrorDetail {
  error_id: string;
  timestamp: string;
  error_type: string;
  message: string;
  traceback: string;
  category: string;
  severity: string;
  component: string;
  source?: string;
  user_id?: string;
  request_id?: string;
  context: Record<string, any>;
}

interface ErrorFilterOptions {
  category?: string;
  severity?: string;
  component?: string;
}

// Helper function to format timestamp
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

// Severity color mapping
const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case ErrorSeverity.DEBUG:
      return 'info';
    case ErrorSeverity.INFO:
      return 'success';
    case ErrorSeverity.WARNING:
      return 'warning';
    case ErrorSeverity.ERROR:
      return 'error';
    case ErrorSeverity.CRITICAL:
      return 'error';
    default:
      return 'default';
  }
};

// Severity icon mapping
const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case ErrorSeverity.DEBUG:
    case ErrorSeverity.INFO:
      return <InfoIcon fontSize="small" />;
    case ErrorSeverity.WARNING:
      return <WarningIcon fontSize="small" />;
    case ErrorSeverity.ERROR:
    case ErrorSeverity.CRITICAL:
      return <ErrorIcon fontSize="small" />;
    default:
      return <BugReportIcon fontSize="small" />;
  }
};

const ErrorMonitor: React.FC = () => {
  // State for error data
  const [errors, setErrors] = useState<ErrorDetail[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // State for error filters
  const [filters, setFilters] = useState<ErrorFilterOptions>({});
  
  // State for error detail dialog
  const [selectedError, setSelectedError] = useState<ErrorDetail | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState<boolean>(false);
  
  // State for error categories and severities
  const [categories, setCategories] = useState<string[]>([]);
  const [severities, setSeverities] = useState<string[]>([]);
  
  // State for snackbar
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'info' | 'warning' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });
  
  // Load error data
  const fetchErrors = async () => {
    setLoading(true);
    try {
      // Build query parameters based on filters
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.component) params.append('component', filters.component);
      
      // Fetch error data
      const response = await api.get<ErrorDetail[]>(`/api/error-logging/recent?${params.toString()}`);
      setErrors(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load error data. Please try again later.');
      console.error('Error fetching error data:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Load error categories and severities
  const fetchMetadata = async () => {
    try {
      const [categoriesResponse, severitiesResponse] = await Promise.all([
        api.get<string[]>('/api/error-logging/categories'),
        api.get<string[]>('/api/error-logging/severities'),
      ]);
      
      setCategories(categoriesResponse.data);
      setSeverities(severitiesResponse.data);
    } catch (err) {
      console.error('Error fetching error metadata:', err);
    }
  };
  
  // Initial data loading
  useEffect(() => {
    fetchErrors();
    fetchMetadata();
    
    // Set up polling to refresh error data every 30 seconds
    const intervalId = setInterval(fetchErrors, 30000);
    return () => clearInterval(intervalId);
  }, []);
  
  // Reload when filters change
  useEffect(() => {
    fetchErrors();
  }, [filters]);
  
  // Handle filter changes
  const handleFilterChange = (name: keyof ErrorFilterOptions, value: string | undefined) => {
    setFilters(prev => ({
      ...prev,
      [name]: value === 'all' ? undefined : value,
    }));
  };
  
  // Handle error detail viewing
  const handleViewErrorDetail = async (errorId: string) => {
    try {
      const response = await api.get<ErrorDetail>(`/api/error-logging/errors/${errorId}`);
      setSelectedError(response.data);
      setDetailDialogOpen(true);
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to load error details',
        severity: 'error',
      });
    }
  };
  
  // Handle snackbar close
  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };
  
  // Render error monitor UI
  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h5" gutterBottom>
        Error Monitor
      </Typography>
      
      {/* Error filters */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Filters
        </Typography>
        <Grid container spacing={2}>
          {/* Category filter */}
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={filters.category || 'all'}
                onChange={(e) => handleFilterChange('category', e.target.value as string)}
              >
                <MenuItem value="all">All Categories</MenuItem>
                {categories.map(category => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Severity filter */}
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>Severity</InputLabel>
              <Select
                label="Severity"
                value={filters.severity || 'all'}
                onChange={(e) => handleFilterChange('severity', e.target.value as string)}
              >
                <MenuItem value="all">All Severities</MenuItem>
                {severities.map(severity => (
                  <MenuItem key={severity} value={severity}>
                    {severity}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Component filter */}
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>Component</InputLabel>
              <Select
                label="Component"
                value={filters.component || 'all'}
                onChange={(e) => handleFilterChange('component', e.target.value as string)}
              >
                <MenuItem value="all">All Components</MenuItem>
                <MenuItem value="frontend">Frontend</MenuItem>
                <MenuItem value="backend">Backend</MenuItem>
                <MenuItem value="api">API</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        
        {/* Refresh button */}
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            onClick={() => fetchErrors()}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Paper>
      
      {/* Error table */}
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Component</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    Loading error data...
                  </TableCell>
                </TableRow>
              ) : errors.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No errors found
                  </TableCell>
                </TableRow>
              ) : (
                errors.map(err => (
                  <TableRow key={err.error_id}>
                    <TableCell>{formatTimestamp(err.timestamp)}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getSeverityIcon(err.severity)}
                        label={err.severity}
                        color={getSeverityColor(err.severity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{err.category}</TableCell>
                    <TableCell>{err.component}</TableCell>
                    <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {err.message}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        onClick={() => handleViewErrorDetail(err.error_id)}
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {/* Error detail dialog */}
      <Dialog 
        open={detailDialogOpen} 
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedError && (
          <>
            <DialogTitle>
              Error Details: {selectedError.error_type}
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Message
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                    <Typography variant="body2">{selectedError.message}</Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Error ID</Typography>
                  <Typography variant="body2">{selectedError.error_id}</Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Timestamp</Typography>
                  <Typography variant="body2">{formatTimestamp(selectedError.timestamp)}</Typography>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography variant="subtitle2">Severity</Typography>
                  <Chip
                    icon={getSeverityIcon(selectedError.severity)}
                    label={selectedError.severity}
                    color={getSeverityColor(selectedError.severity) as any}
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography variant="subtitle2">Category</Typography>
                  <Typography variant="body2">{selectedError.category}</Typography>
                </Grid>
                
                <Grid item xs={12} sm={4}>
                  <Typography variant="subtitle2">Component</Typography>
                  <Typography variant="body2">{selectedError.component}</Typography>
                </Grid>
                
                {selectedError.source && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2">Source</Typography>
                    <Typography variant="body2">{selectedError.source}</Typography>
                  </Grid>
                )}
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Stack Trace</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <TextField
                        fullWidth
                        multiline
                        rows={10}
                        variant="outlined"
                        value={selectedError.traceback}
                        InputProps={{ readOnly: true }}
                      />
                    </AccordionDetails>
                  </Accordion>
                </Grid>
                
                <Grid item xs={12}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Context Data</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <TextField
                        fullWidth
                        multiline
                        rows={5}
                        variant="outlined"
                        value={JSON.stringify(selectedError.context, null, 2)}
                        InputProps={{ readOnly: true }}
                      />
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailDialogOpen(false)}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ErrorMonitor;
