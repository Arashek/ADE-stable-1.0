import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography
} from '@mui/material';
import {
  DeleteOutline,
  ErrorOutline,
  FilterList,
  InfoOutlined,
  Refresh,
  Search,
  Warning,
  WarningAmber
} from '@mui/icons-material';
import axios from 'axios';
import { ErrorCategory, ErrorSeverity } from '../../services/errorHandling';

// Types for error logs
interface ErrorLog {
  id: string;
  timestamp: string;
  message: string;
  category: string;
  severity: string;
  component: string;
  context?: Record<string, any>;
  stack_trace?: string;
}

interface ErrorStats {
  total: number;
  bySeverity: Record<string, number>;
  byCategory: Record<string, number>;
  recentErrors: number;
  topComponents: Array<{component: string, count: number}>;
}

// Configuration
const API_URL = 'http://localhost:8000';
const DEFAULT_PAGE_SIZE = 10;

/**
 * Error Logs Viewer component for the admin dashboard
 */
const ErrorLogsViewer: React.FC = () => {
  // State
  const [loading, setLoading] = useState<boolean>(false);
  const [errors, setErrors] = useState<ErrorLog[]>([]);
  const [filteredErrors, setFilteredErrors] = useState<ErrorLog[]>([]);
  const [stats, setStats] = useState<ErrorStats | null>(null);
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(DEFAULT_PAGE_SIZE);
  const [selectedError, setSelectedError] = useState<ErrorLog | null>(null);
  const [filters, setFilters] = useState({
    severity: 'all',
    category: 'all',
    component: 'all',
    search: ''
  });
  const [components, setComponents] = useState<string[]>([]);
  
  // Load initial data
  useEffect(() => {
    fetchErrors();
  }, []);
  
  // Apply filters when they change
  useEffect(() => {
    filterErrors();
  }, [errors, filters]);
  
  // Extract components when errors change
  useEffect(() => {
    if (errors.length > 0) {
      const uniqueComponents = Array.from(new Set(errors.map(err => err.component)));
      setComponents(uniqueComponents);
    }
  }, [errors]);
  
  // Fetch errors from the API
  const fetchErrors = async () => {
    setLoading(true);
    
    try {
      const response = await axios.get(`${API_URL}/api/errors`);
      setErrors(response.data.errors || []);
      setStats(response.data.stats || null);
    } catch (error) {
      console.error('Failed to fetch error logs:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Apply filters to the errors
  const filterErrors = () => {
    let filtered = [...errors];
    
    // Filter by severity
    if (filters.severity !== 'all') {
      filtered = filtered.filter(err => err.severity === filters.severity);
    }
    
    // Filter by category
    if (filters.category !== 'all') {
      filtered = filtered.filter(err => err.category === filters.category);
    }
    
    // Filter by component
    if (filters.component !== 'all') {
      filtered = filtered.filter(err => err.component === filters.component);
    }
    
    // Filter by search term
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(err => 
        err.message.toLowerCase().includes(searchTerm) || 
        (err.stack_trace && err.stack_trace.toLowerCase().includes(searchTerm)) ||
        (err.context && JSON.stringify(err.context).toLowerCase().includes(searchTerm))
      );
    }
    
    // Sort by timestamp (newest first)
    filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    setFilteredErrors(filtered);
    setPage(0); // Reset to first page when filters change
  };
  
  // Clear all error logs
  const clearAllErrors = async () => {
    if (!window.confirm('Are you sure you want to clear all error logs? This action cannot be undone.')) {
      return;
    }
    
    setLoading(true);
    
    try {
      await axios.delete(`${API_URL}/api/errors`);
      setErrors([]);
      setFilteredErrors([]);
      setStats(null);
    } catch (error) {
      console.error('Failed to clear error logs:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Generate mock data for testing
  const generateTestData = async () => {
    setLoading(true);
    
    try {
      await axios.post(`${API_URL}/api/errors/generate-test-data`);
      fetchErrors();
    } catch (error) {
      console.error('Failed to generate test data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Change page
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };
  
  // Change rows per page
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // View error details
  const handleViewError = (error: ErrorLog) => {
    setSelectedError(error);
  };
  
  // Close error details dialog
  const handleCloseDialog = () => {
    setSelectedError(null);
  };
  
  // Handle filter changes
  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Render severity badge with appropriate color
  const renderSeverityBadge = (severity: string) => {
    let color = 'primary';
    let icon = <InfoOutlined />;
    
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        color = 'error';
        icon = <ErrorOutline />;
        break;
      case ErrorSeverity.ERROR:
        color = 'error';
        icon = <ErrorOutline />;
        break;
      case ErrorSeverity.WARNING:
        color = 'warning';
        icon = <Warning />;
        break;
      case ErrorSeverity.INFO:
        color = 'info';
        icon = <InfoOutlined />;
        break;
      default:
        break;
    }
    
    return (
      <Chip
        icon={icon}
        label={severity}
        color={color as any}
        size="small"
        variant="outlined"
      />
    );
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return timestamp;
    }
  };
  
  // Render category badge
  const renderCategoryBadge = (category: string) => {
    return (
      <Chip
        label={category}
        size="small"
        variant="outlined"
      />
    );
  };
  
  // Render statistics dashboard
  const renderStatsDashboard = () => {
    if (!stats) return null;
    
    return (
      <Box mb={3}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Error Statistics
          </Typography>
          
          <Grid container spacing={2}>
            {/* Total errors */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Errors
                  </Typography>
                  <Typography variant="h4">
                    {stats.total}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Recent errors (last 24h) */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Recent Errors (24h)
                  </Typography>
                  <Typography variant="h4">
                    {stats.recentErrors}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Critical/Error count */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Critical/Errors
                  </Typography>
                  <Typography variant="h4">
                    {(stats.bySeverity[ErrorSeverity.CRITICAL] || 0) + 
                     (stats.bySeverity[ErrorSeverity.ERROR] || 0)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Top component with errors */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Top Component
                  </Typography>
                  <Typography variant="h6" noWrap>
                    {stats.topComponents && stats.topComponents.length > 0 
                      ? `${stats.topComponents[0].component} (${stats.topComponents[0].count})`
                      : 'None'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          {/* Severity breakdown */}
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Errors by Severity
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {Object.entries(stats.bySeverity).map(([severity, count]) => (
                <Chip 
                  key={severity}
                  label={`${severity}: ${count}`}
                  onClick={() => handleFilterChange('severity', severity)}
                  clickable
                  size="small"
                  color={severity === ErrorSeverity.CRITICAL || severity === ErrorSeverity.ERROR 
                    ? 'error' 
                    : severity === ErrorSeverity.WARNING 
                      ? 'warning' 
                      : 'info'}
                />
              ))}
            </Stack>
          </Box>
          
          {/* Category breakdown */}
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Errors by Category
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {Object.entries(stats.byCategory).map(([category, count]) => (
                <Chip 
                  key={category}
                  label={`${category}: ${count}`}
                  onClick={() => handleFilterChange('category', category)}
                  clickable
                  size="small"
                />
              ))}
            </Stack>
          </Box>
        </Paper>
      </Box>
    );
  };
  
  return (
    <Box>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h5">
          Error Logs
        </Typography>
        
        <Box>
          <Button 
            startIcon={<Refresh />}
            onClick={fetchErrors}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          
          <Button 
            startIcon={<DeleteOutline />}
            onClick={clearAllErrors}
            disabled={loading || errors.length === 0}
            color="error"
            variant="outlined"
            sx={{ mr: 1 }}
          >
            Clear All
          </Button>
          
          <Button 
            onClick={generateTestData}
            disabled={loading}
            variant="outlined"
          >
            Generate Test Data
          </Button>
        </Box>
      </Box>
      
      {/* Statistics Dashboard */}
      {renderStatsDashboard()}
      
      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <FilterList sx={{ mr: 1 }} />
          <Typography variant="subtitle1">
            Filters
          </Typography>
        </Box>
        
        <Grid container spacing={2}>
          {/* Severity filter */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Severity</InputLabel>
              <Select
                value={filters.severity}
                label="Severity"
                onChange={(e) => handleFilterChange('severity', e.target.value)}
              >
                <MenuItem value="all">All Severities</MenuItem>
                <MenuItem value={ErrorSeverity.CRITICAL}>Critical</MenuItem>
                <MenuItem value={ErrorSeverity.ERROR}>Error</MenuItem>
                <MenuItem value={ErrorSeverity.WARNING}>Warning</MenuItem>
                <MenuItem value={ErrorSeverity.INFO}>Info</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Category filter */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={filters.category}
                label="Category"
                onChange={(e) => handleFilterChange('category', e.target.value)}
              >
                <MenuItem value="all">All Categories</MenuItem>
                <MenuItem value={ErrorCategory.AGENT}>Agent</MenuItem>
                <MenuItem value={ErrorCategory.API}>API</MenuItem>
                <MenuItem value={ErrorCategory.FRONTEND}>Frontend</MenuItem>
                <MenuItem value={ErrorCategory.SYSTEM}>System</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Component filter */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Component</InputLabel>
              <Select
                value={filters.component}
                label="Component"
                onChange={(e) => handleFilterChange('component', e.target.value)}
              >
                <MenuItem value="all">All Components</MenuItem>
                {components.map(component => (
                  <MenuItem key={component} value={component}>{component}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Search filter */}
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              size="small"
              label="Search"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              InputProps={{
                endAdornment: <Search />
              }}
            />
          </Grid>
        </Grid>
      </Paper>
      
      {/* Error Table */}
      <Paper elevation={3}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Severity</TableCell>
                <TableCell>Time</TableCell>
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
                    <CircularProgress size={40} sx={{ my: 2 }} />
                  </TableCell>
                </TableRow>
              ) : filteredErrors.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" sx={{ py: 2 }}>
                      No error logs found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredErrors
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((error) => (
                    <TableRow key={error.id} hover>
                      <TableCell>{renderSeverityBadge(error.severity)}</TableCell>
                      <TableCell>{formatTimestamp(error.timestamp)}</TableCell>
                      <TableCell>{renderCategoryBadge(error.category)}</TableCell>
                      <TableCell>{error.component}</TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                          {error.message}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => handleViewError(error)}>
                            <InfoOutlined fontSize="small" />
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
          count={filteredErrors.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      
      {/* Error Details Dialog */}
      <Dialog
        open={!!selectedError}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        {selectedError && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center">
                <Box mr={1}>
                  {selectedError.severity === ErrorSeverity.CRITICAL || selectedError.severity === ErrorSeverity.ERROR ? (
                    <ErrorOutline color="error" />
                  ) : selectedError.severity === ErrorSeverity.WARNING ? (
                    <WarningAmber color="warning" />
                  ) : (
                    <InfoOutlined color="info" />
                  )}
                </Box>
                Error Details
                <Box ml={1}>
                  {renderSeverityBadge(selectedError.severity)}
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Message
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="body1">
                      {selectedError.message}
                    </Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Metadata
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography variant="body2">
                      <strong>ID:</strong> {selectedError.id}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Time:</strong> {formatTimestamp(selectedError.timestamp)}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Category:</strong> {selectedError.category}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Component:</strong> {selectedError.component}
                    </Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Context
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', maxHeight: 150, overflow: 'auto' }}>
                    {selectedError.context ? (
                      <pre style={{ margin: 0, fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(selectedError.context, null, 2)}
                      </pre>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No context available
                      </Typography>
                    )}
                  </Paper>
                </Grid>
                
                {selectedError.stack_trace && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>
                      Stack Trace
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', maxHeight: 300, overflow: 'auto' }}>
                      <pre style={{ margin: 0, fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>
                        {selectedError.stack_trace}
                      </pre>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default ErrorLogsViewer;
