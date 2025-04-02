import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  SelectChangeEvent,
  InputAdornment,
  useTheme,
  alpha
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon,
  ErrorOutline as ErrorOutlineIcon,
  NotificationsActive as NotificationsActiveIcon,
  Code as CodeIcon,
  MoreVert as MoreVertIcon,
  ArrowDropDown as ArrowDropDownIcon,
  ArrowDropUp as ArrowDropUpIcon
} from '@mui/icons-material';
import { Agent } from '../AgentListPanel';

// Error severity enum (matching backend)
export enum ErrorSeverity {
  CRITICAL = 'CRITICAL',
  ERROR = 'ERROR',
  WARNING = 'WARNING',
  INFO = 'INFO'
}

// Error category enum (matching backend)
export enum ErrorCategory {
  AGENT = 'AGENT',
  API = 'API',
  FRONTEND = 'FRONTEND',
  BACKEND = 'BACKEND',
  DATABASE = 'DATABASE',
  SECURITY = 'SECURITY',
  SYSTEM = 'SYSTEM'
}

// Error log interface
export interface ErrorLog {
  id: string;
  timestamp: Date;
  severity: ErrorSeverity;
  category: ErrorCategory;
  agentId?: string;
  message: string;
  stackTrace?: string;
  context?: Record<string, any>;
  resolved: boolean;
  resolvedAt?: Date;
  resolvedBy?: string;
  occurrences: number;
}

interface ErrorAnalyticsPanelProps {
  agents: Agent[];
  selectedAgentId?: string;
}

/**
 * Helper function to generate mock error logs for development
 */
const generateMockErrorLogs = (agents: Agent[], count: number = 50): ErrorLog[] => {
  const logs: ErrorLog[] = [];
  const severities = Object.values(ErrorSeverity);
  const categories = Object.values(ErrorCategory);
  
  // Error message templates
  const errorMessages = [
    'Failed to connect to external API',
    'Unable to process request due to invalid input',
    'Timeout occurred during operation',
    'Resource not found',
    'Unexpected response format',
    'Authentication failed',
    'Permission denied for operation',
    'Database query error',
    'Network connection interrupted',
    'Memory allocation failure'
  ];
  
  // Context templates
  const contextTemplates = [
    { endpoint: '/api/v1/agents', method: 'GET', statusCode: 404 },
    { operation: 'code_analysis', duration: 2500, memoryUsage: '256MB' },
    { component: 'TaskProcessor', action: 'execute', taskId: 'task-123' },
    { service: 'AuthService', userId: 'user-456', requestId: 'req-789' },
    { module: 'DataTransformer', inputSize: '2.5MB', outputSize: '0' }
  ];
  
  // Generate random error logs
  for (let i = 0; i < count; i++) {
    const timestamp = new Date(Date.now() - Math.floor(Math.random() * 14 * 24 * 60 * 60 * 1000)); // Within last 2 weeks
    const severity = severities[Math.floor(Math.random() * severities.length)];
    const category = categories[Math.floor(Math.random() * categories.length)];
    const messageIndex = Math.floor(Math.random() * errorMessages.length);
    const message = `${errorMessages[messageIndex]} [code: E${(1000 + i).toString()}]`;
    
    // Randomly assign to an agent for agent-related errors
    let agentId;
    if (category === ErrorCategory.AGENT || Math.random() > 0.5) {
      const agent = agents[Math.floor(Math.random() * agents.length)];
      agentId = agent.id;
    }
    
    // Random context
    const contextTemplate = contextTemplates[Math.floor(Math.random() * contextTemplates.length)];
    const context = { ...contextTemplate, sessionId: `sess-${Math.floor(Math.random() * 1000)}` };
    
    // Random stack trace for more severe errors
    let stackTrace;
    if (severity === ErrorSeverity.CRITICAL || severity === ErrorSeverity.ERROR) {
      stackTrace = `Error: ${message}\n  at processRequest (${category.toLowerCase()}.js:${Math.floor(Math.random() * 500) + 100})\n  at handleOperation (core.js:${Math.floor(Math.random() * 300) + 50})\n  at executeTask (tasks.js:${Math.floor(Math.random() * 200) + 20})`;
    }
    
    // Randomly mark some as resolved
    const resolved = Math.random() > 0.7;
    let resolvedAt, resolvedBy;
    if (resolved) {
      resolvedAt = new Date(timestamp.getTime() + Math.floor(Math.random() * 24 * 60 * 60 * 1000)); // Resolved within 24 hours
      resolvedBy = Math.random() > 0.5 ? 'system' : 'admin';
    }
    
    // Random occurrence count
    const occurrences = Math.floor(Math.random() * 10) + 1;
    
    logs.push({
      id: `error-${i}`,
      timestamp,
      severity,
      category,
      agentId,
      message,
      stackTrace,
      context,
      resolved,
      resolvedAt,
      resolvedBy,
      occurrences
    });
  }
  
  return logs;
};

/**
 * ErrorAnalyticsPanel Component - Displays error analytics and logs for agents
 */
const ErrorAnalyticsPanel: React.FC<ErrorAnalyticsPanelProps> = ({
  agents,
  selectedAgentId
}) => {
  const theme = useTheme();
  
  // Generate mock error logs
  const [errorLogs, setErrorLogs] = useState<ErrorLog[]>(generateMockErrorLogs(agents));
  
  // Selected error log
  const [selectedErrorId, setSelectedErrorId] = useState<string | null>(null);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<ErrorSeverity | ''>('');
  const [categoryFilter, setCategoryFilter] = useState<ErrorCategory | ''>('');
  const [resolvedFilter, setResolvedFilter] = useState<boolean | null>(null);
  const [timeRangeFilter, setTimeRangeFilter] = useState<'day' | 'week' | 'month' | 'all'>('week');
  
  // Calculate date range for filtering
  const getDateRangeFilter = () => {
    const now = new Date();
    const startDate = new Date();
    
    switch (timeRangeFilter) {
      case 'day':
        startDate.setDate(now.getDate() - 1);
        break;
      case 'week':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case 'all':
      default:
        return null;
    }
    
    return startDate;
  };
  
  // Filter error logs
  const filteredErrorLogs = errorLogs.filter(log => {
    // Filter by selected agent if any
    const agentFilter = selectedAgentId 
      ? log.agentId === selectedAgentId
      : true;
      
    // Filter by search term
    const searchFilter = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.stackTrace && log.stackTrace.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Filter by severity
    const severityFilterMatch = severityFilter === '' || log.severity === severityFilter;
    
    // Filter by category
    const categoryFilterMatch = categoryFilter === '' || log.category === categoryFilter;
    
    // Filter by resolved status
    const resolvedFilterMatch = resolvedFilter === null || log.resolved === resolvedFilter;
    
    // Filter by date range
    const dateRangeFilter = getDateRangeFilter();
    const dateFilterMatch = !dateRangeFilter || log.timestamp >= dateRangeFilter;
    
    return agentFilter && searchFilter && severityFilterMatch && categoryFilterMatch && resolvedFilterMatch && dateFilterMatch;
  });
  
  // Sort logs by timestamp (newest first)
  const sortedErrorLogs = [...filteredErrorLogs].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  
  // Get selected error log
  const selectedError = selectedErrorId ? errorLogs.find(log => log.id === selectedErrorId) : null;
  
  // Format date
  const formatDate = (date: Date): string => {
    return date.toLocaleString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  // Get agent by ID
  const getAgentById = (id?: string) => {
    if (!id) return null;
    return agents.find(agent => agent.id === id);
  };
  
  // Get severity icon
  const getSeverityIcon = (severity: ErrorSeverity) => {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
      case ErrorSeverity.ERROR:
        return <ErrorIcon fontSize="small" color="error" />;
      case ErrorSeverity.WARNING:
        return <WarningIcon fontSize="small" color="warning" />;
      case ErrorSeverity.INFO:
        return <InfoIcon fontSize="small" color="info" />;
      default:
        return <InfoIcon fontSize="small" />;
    }
  };
  
  // Get severity color
  const getSeverityColor = (severity: ErrorSeverity) => {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        return theme.palette.error.dark;
      case ErrorSeverity.ERROR:
        return theme.palette.error.main;
      case ErrorSeverity.WARNING:
        return theme.palette.warning.main;
      case ErrorSeverity.INFO:
        return theme.palette.info.main;
      default:
        return theme.palette.grey[500];
    }
  };
  
  // Handle severity filter change
  const handleSeverityFilterChange = (event: SelectChangeEvent<ErrorSeverity | ''>) => {
    setSeverityFilter(event.target.value as ErrorSeverity | '');
  };
  
  // Handle category filter change
  const handleCategoryFilterChange = (event: SelectChangeEvent<ErrorCategory | ''>) => {
    setCategoryFilter(event.target.value as ErrorCategory | '');
  };
  
  // Handle time range filter change
  const handleTimeRangeFilterChange = (range: 'day' | 'week' | 'month' | 'all') => {
    setTimeRangeFilter(range);
  };
  
  // Reset all filters
  const handleResetFilters = () => {
    setSearchTerm('');
    setSeverityFilter('');
    setCategoryFilter('');
    setResolvedFilter(null);
    setTimeRangeFilter('week');
  };
  
  // Handle refresh
  const handleRefresh = () => {
    setErrorLogs(generateMockErrorLogs(agents));
  };
  
  // Calculate error statistics
  const calculateErrorStats = () => {
    const totalErrors = errorLogs.length;
    const unresolvedErrors = errorLogs.filter(log => !log.resolved).length;
    const criticalErrors = errorLogs.filter(log => log.severity === ErrorSeverity.CRITICAL).length;
    const errorsByCategory = Object.values(ErrorCategory).map(category => ({
      category,
      count: errorLogs.filter(log => log.category === category).length
    }));
    const errorsBySeverity = Object.values(ErrorSeverity).map(severity => ({
      severity,
      count: errorLogs.filter(log => log.severity === severity).length
    }));
    
    return {
      totalErrors,
      unresolvedErrors,
      criticalErrors,
      errorsByCategory,
      errorsBySeverity
    };
  };
  
  const errorStats = calculateErrorStats();
  
  // Render error summary cards
  const renderErrorSummaryCards = () => {
    return (
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={0} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Total Errors
            </Typography>
            <Typography variant="h4">
              {errorStats.totalErrors}
            </Typography>
            <Chip 
              size="small" 
              label={`${unresolvedPercentage}% unresolved`} 
              color="primary" 
              sx={{ mt: 1 }} 
            />
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={0} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Unresolved Errors
            </Typography>
            <Typography variant="h4" color={errorStats.unresolvedErrors > 0 ? 'error' : 'textPrimary'}>
              {errorStats.unresolvedErrors}
            </Typography>
            <Chip 
              size="small" 
              icon={<ErrorOutlineIcon fontSize="small" />}
              label="Require attention" 
              color="error" 
              variant="outlined"
              sx={{ mt: 1 }} 
            />
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={0} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Critical Errors
            </Typography>
            <Typography variant="h4" color={errorStats.criticalErrors > 0 ? 'error' : 'textPrimary'}>
              {errorStats.criticalErrors}
            </Typography>
            <Chip 
              size="small" 
              icon={<NotificationsActiveIcon fontSize="small" />}
              label="High priority" 
              color="error" 
              sx={{ mt: 1 }} 
            />
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={0} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Most Common Category
            </Typography>
            <Typography variant="h4">
              {mostCommonCategory.category}
            </Typography>
            <Chip 
              size="small" 
              label={`${mostCommonCategory.count} occurrences`} 
              color="primary" 
              variant="outlined"
              sx={{ mt: 1 }} 
            />
          </Paper>
        </Grid>
      </Grid>
    );
  };
  
  // Calculate derived statistics
  const unresolvedPercentage = Math.round((errorStats.unresolvedErrors / errorStats.totalErrors) * 100) || 0;
  const mostCommonCategory = errorStats.errorsByCategory.reduce((max, current) => 
    current.count > max.count ? current : max, 
    { category: 'NONE', count: 0 }
  );

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with controls */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Error Analytics
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<FilterListIcon />}
            onClick={handleResetFilters}
          >
            {(searchTerm || severityFilter || categoryFilter || resolvedFilter !== null) 
              ? 'Clear Filters' 
              : 'Filter'}
          </Button>
          
          <IconButton size="small" onClick={handleRefresh}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>
      
      {/* Error statistics summary */}
      <Box sx={{ mb: 3 }}>
        {renderErrorSummaryCards()}
      </Box>
      
      {/* Filters */}
      <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        <TextField
          variant="outlined"
          size="small"
          placeholder="Search errors..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, minWidth: 200 }}
        />
        
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="severity-filter-label">Severity</InputLabel>
          <Select
            labelId="severity-filter-label"
            id="severity-filter"
            value={severityFilter}
            label="Severity"
            onChange={handleSeverityFilterChange}
          >
            <MenuItem value="">All Severities</MenuItem>
            {Object.values(ErrorSeverity).map((severity) => (
              <MenuItem key={severity} value={severity}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {getSeverityIcon(severity)}
                  <Typography sx={{ ml: 1 }}>{severity}</Typography>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="category-filter-label">Category</InputLabel>
          <Select
            labelId="category-filter-label"
            id="category-filter"
            value={categoryFilter}
            label="Category"
            onChange={handleCategoryFilterChange}
          >
            <MenuItem value="">All Categories</MenuItem>
            {Object.values(ErrorCategory).map((category) => (
              <MenuItem key={category} value={category}>{category}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Box>
          <Button
            size="small"
            variant={resolvedFilter === false ? 'contained' : 'outlined'}
            onClick={() => setResolvedFilter(resolvedFilter === false ? null : false)}
            sx={{ mr: 1 }}
          >
            Unresolved
          </Button>
          <Button
            size="small"
            variant={resolvedFilter === true ? 'contained' : 'outlined'}
            onClick={() => setResolvedFilter(resolvedFilter === true ? null : true)}
          >
            Resolved
          </Button>
        </Box>
        
        <Box>
          <Button
            size="small"
            variant={timeRangeFilter === 'day' ? 'contained' : 'outlined'}
            onClick={() => handleTimeRangeFilterChange('day')}
            sx={{ mr: 1 }}
          >
            24h
          </Button>
          <Button
            size="small"
            variant={timeRangeFilter === 'week' ? 'contained' : 'outlined'}
            onClick={() => handleTimeRangeFilterChange('week')}
            sx={{ mr: 1 }}
          >
            7d
          </Button>
          <Button
            size="small"
            variant={timeRangeFilter === 'month' ? 'contained' : 'outlined'}
            onClick={() => handleTimeRangeFilterChange('month')}
            sx={{ mr: 1 }}
          >
            30d
          </Button>
          <Button
            size="small"
            variant={timeRangeFilter === 'all' ? 'contained' : 'outlined'}
            onClick={() => handleTimeRangeFilterChange('all')}
          >
            All
          </Button>
        </Box>
      </Box>
      
      {/* Main content */}
      <Box sx={{ flexGrow: 1, display: 'flex', gap: 2, overflow: 'hidden' }}>
        {/* Error list */}
        <Box sx={{ width: '40%', height: '100%', overflow: 'auto' }}>
          <Paper elevation={0} variant="outlined" sx={{ height: '100%' }}>
            <List sx={{ padding: 0 }}>
              {sortedErrorLogs.length === 0 ? (
                <ListItem>
                  <ListItemText 
                    primary="No errors found" 
                    secondary="Try adjusting your filters"
                  />
                </ListItem>
              ) : (
                sortedErrorLogs.map(log => (
                  <ListItem 
                    key={log.id}
                    button
                    selected={selectedErrorId === log.id}
                    onClick={() => setSelectedErrorId(log.id)}
                    sx={{ 
                      borderLeft: `4px solid ${getSeverityColor(log.severity)}`,
                      opacity: log.resolved ? 0.7 : 1,
                      '&.Mui-selected': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                      },
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.05),
                      }
                    }}
                  >
                    <ListItemIcon>
                      {getSeverityIcon(log.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography 
                            variant="subtitle2"
                            sx={{ 
                              textDecoration: log.resolved ? 'line-through' : 'none',
                              maxWidth: '70%',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {log.message}
                          </Typography>
                          <Chip 
                            size="small"
                            label={log.category}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <React.Fragment>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                            <Typography variant="caption" color="textSecondary">
                              {formatDate(log.timestamp)}
                            </Typography>
                            {log.occurrences > 1 && (
                              <Chip
                                size="small"
                                label={`${log.occurrences} occurrences`}
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                          </Box>
                          {log.agentId && (
                            <Typography variant="caption" color="textSecondary" display="block">
                              Agent: {getAgentById(log.agentId)?.name || log.agentId}
                            </Typography>
                          )}
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                ))
              )}
            </List>
          </Paper>
        </Box>
        
        {/* Error details */}
        <Box sx={{ width: '60%', height: '100%', overflow: 'auto' }}>
          {!selectedError ? (
            <Paper
              elevation={0}
              variant="outlined"
              sx={{
                height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                borderStyle: 'dashed'
              }}
            >
              <Box sx={{ textAlign: 'center', p: 3 }}>
                <ErrorOutlineIcon color="disabled" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="body1" color="textSecondary">
                  Select an error to view details
                </Typography>
              </Box>
            </Paper>
          ) : (
            <Paper
              elevation={0}
              variant="outlined"
              sx={{ height: '100%', p: 2 }}
            >
              <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                    {getSeverityIcon(selectedError.severity)}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      {selectedError.severity} {selectedError.category} Error
                    </Typography>
                  </Box>
                  <Typography variant="subtitle1">
                    {selectedError.message}
                  </Typography>
                  <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip 
                      size="small" 
                      label={`${formatDate(selectedError.timestamp)}`}
                      variant="outlined"
                    />
                    {selectedError.agentId && (
                      <Chip 
                        size="small" 
                        label={`Agent: ${getAgentById(selectedError.agentId)?.name || selectedError.agentId}`}
                        variant="outlined"
                      />
                    )}
                    {selectedError.occurrences > 1 && (
                      <Chip 
                        size="small" 
                        label={`${selectedError.occurrences} occurrences`}
                        variant="outlined"
                      />
                    )}
                    {selectedError.resolved && (
                      <Chip 
                        size="small" 
                        label={`Resolved: ${formatDate(selectedError.resolvedAt!)}`}
                        color="success"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>
                <Button
                  variant={selectedError.resolved ? 'outlined' : 'contained'}
                  color={selectedError.resolved ? 'primary' : 'success'}
                  size="small"
                  onClick={() => {
                    // Toggle resolved status
                    setErrorLogs(prev => prev.map(log => 
                      log.id === selectedError.id 
                        ? { 
                            ...log, 
                            resolved: !log.resolved,
                            resolvedAt: !log.resolved ? new Date() : undefined,
                            resolvedBy: !log.resolved ? 'admin' : undefined
                          } 
                        : log
                    ));
                  }}
                >
                  {selectedError.resolved ? 'Mark Unresolved' : 'Mark Resolved'}
                </Button>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              {/* Stack trace */}
              {selectedError.stackTrace && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Stack Trace
                  </Typography>
                  <Paper 
                    elevation={0}
                    sx={{ 
                      p: 2, 
                      backgroundColor: alpha(theme.palette.background.default, 0.5),
                      fontFamily: 'monospace',
                      fontSize: '0.85rem',
                      whiteSpace: 'pre-wrap',
                      overflowX: 'auto',
                      maxHeight: 200,
                      overflowY: 'auto'
                    }}
                  >
                    {selectedError.stackTrace}
                  </Paper>
                </Box>
              )}
              
              {/* Context */}
              {selectedError.context && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Context
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(selectedError.context).map(([key, value]) => (
                      <Grid item xs={12} sm={6} md={4} key={key}>
                        <Paper elevation={0} sx={{ p: 2, backgroundColor: alpha(theme.palette.background.default, 0.5) }}>
                          <Typography variant="caption" color="textSecondary">
                            {key}
                          </Typography>
                          <Typography variant="body2">
                            {String(value)}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
              
              {/* Suggested resolution - for future enhancement */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Suggested Resolution
                </Typography>
                <Paper elevation={0} sx={{ p: 2, backgroundColor: alpha(theme.palette.primary.main, 0.05) }}>
                  <Typography variant="body2">
                    {selectedError.severity === ErrorSeverity.CRITICAL 
                      ? 'This is a critical error that requires immediate attention. Check the affected component and the associated agent for further diagnostics.'
                      : selectedError.severity === ErrorSeverity.ERROR
                      ? 'Investigate the error context and stack trace. This issue may be affecting system functionality and should be addressed promptly.'
                      : selectedError.severity === ErrorSeverity.WARNING
                      ? 'Monitor this warning as it may escalate to an error. Consider addressing the underlying cause in the next maintenance cycle.'
                      : 'This informational message can be reviewed during routine system checks. No immediate action required.'}
                  </Typography>
                </Paper>
              </Box>
            </Paper>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default ErrorAnalyticsPanel;
