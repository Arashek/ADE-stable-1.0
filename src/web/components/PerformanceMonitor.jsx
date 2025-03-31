import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  IconButton,
  Tooltip,
  Collapse,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper as MuiPaper
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  NetworkCheck as NetworkCheckIcon,
  Speed as SpeedIcon,
  WifiTethering as WifiTetheringIcon
} from '@mui/icons-material';
import performanceMonitor from '../utils/performance-monitor';

const PerformanceMonitor = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(true);

  const refreshReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const newReport = performanceMonitor.getReport();
      setReport(newReport);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshReport();
    const interval = setInterval(refreshReport, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleExport = () => {
    performanceMonitor.exportData();
  };

  const renderTimingStats = () => {
    if (!report?.timings) return null;

    return (
      <Grid container spacing={2}>
        {Object.entries(report.timings).map(([name, stats]) => (
          <Grid item xs={12} sm={6} md={4} key={name}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {name}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Average: {stats.average.toFixed(2)}ms
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    P95: {stats.p95.toFixed(2)}ms
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    P99: {stats.p99.toFixed(2)}ms
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min((stats.average / 1000) * 100, 100)}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: stats.average > 1000 ? 'error.main' : 'primary.main'
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  const renderMemoryStats = () => {
    if (!report?.memory) return null;

    const { averageUsed, averageTotal, maxUsed, maxTotal } = report.memory;
    const usagePercentage = (averageUsed / averageTotal) * 100;

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Memory Usage
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Average Used: {(averageUsed / (1024 * 1024)).toFixed(2)} MB
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Average Total: {(averageTotal / (1024 * 1024)).toFixed(2)} MB
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Max Used: {(maxUsed / (1024 * 1024)).toFixed(2)} MB
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Max Total: {(maxTotal / (1024 * 1024)).toFixed(2)} MB
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={usagePercentage}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(0, 0, 0, 0.1)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: usagePercentage > 80 ? 'error.main' : 'primary.main'
              }
            }}
          />
        </CardContent>
      </Card>
    );
  };

  const renderInteractionStats = () => {
    if (!report?.interactions) return null;

    return (
      <Grid container spacing={2}>
        {Object.entries(report.interactions).map(([name, stats]) => (
          <Grid item xs={12} sm={6} md={4} key={name}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Count: {stats.count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average: {stats.average.toFixed(2)}ms
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Max: {stats.max.toFixed(2)}ms
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Min: {stats.min.toFixed(2)}ms
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  const renderErrors = () => {
    if (!report?.errors?.length) return null;

    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Errors
        </Typography>
        {report.errors.map((error, index) => (
          <Alert key={index} severity="error" sx={{ mb: 1 }}>
            {error.message}
          </Alert>
        ))}
      </Box>
    );
  };

  const renderNetworkStats = () => {
    if (!report?.network) return null;

    const { resources, navigation, connection } = report.network;

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <NetworkCheckIcon /> Network Performance
        </Typography>

        {/* Navigation Timing */}
        {navigation && (
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Page Load Performance
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Average Load Time: {navigation.averageLoadTime.toFixed(2)}ms
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      DOM Content Loaded: {navigation.averageDomContentLoaded.toFixed(2)}ms
                    </Typography>
                    {navigation.averageFirstPaint && (
                      <Typography variant="body2" color="text.secondary">
                        First Paint: {navigation.averageFirstPaint.toFixed(2)}ms
                      </Typography>
                    )}
                    {navigation.averageFirstContentfulPaint && (
                      <Typography variant="body2" color="text.secondary">
                        First Contentful Paint: {navigation.averageFirstContentfulPaint.toFixed(2)}ms
                      </Typography>
                    )}
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((navigation.averageLoadTime / 3000) * 100, 100)}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(0, 0, 0, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: navigation.averageLoadTime > 2000 ? 'error.main' : 'primary.main'
                      }
                    }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Resource Loading */}
        {resources && (
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Resource Loading
              </Typography>
              <TableContainer component={MuiPaper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell align="right">Avg Duration</TableCell>
                      <TableCell align="right">Total Size</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(resources).map(([type, stats]) => (
                      <TableRow key={type}>
                        <TableCell>{type}</TableCell>
                        <TableCell align="right">{stats.count}</TableCell>
                        <TableCell align="right">{stats.averageDuration.toFixed(2)}ms</TableCell>
                        <TableCell align="right">{(stats.totalSize / 1024).toFixed(2)}KB</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}

        {/* Connection Info */}
        {connection && (
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <WifiTetheringIcon /> Connection Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Type: {connection.types ? Object.entries(connection.types).map(([type, count]) => `${type} (${count})`).join(', ') : 'Unknown'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Effective Type: {connection.effectiveTypes ? Object.entries(connection.effectiveTypes).map(([type, count]) => `${type} (${count})`).join(', ') : 'Unknown'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average RTT: {connection.averageRtt.toFixed(2)}ms
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average Downlink: {connection.averageDownlink.toFixed(2)}Mbps
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        RTT Quality
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min((connection.averageRtt / 100) * 100, 100)}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: 'rgba(0, 0, 0, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: connection.averageRtt > 50 ? 'error.main' : 'primary.main'
                          }
                        }}
                      />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Downlink Speed
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min((connection.averageDownlink / 10) * 100, 100)}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: 'rgba(0, 0, 0, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: connection.averageDownlink < 1 ? 'error.main' : 'primary.main'
                          }
                        }}
                      />
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ flexGrow: 1 }}>
          Performance Monitor
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={refreshReport} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Export Data">
          <IconButton onClick={handleExport}>
            <DownloadIcon />
          </IconButton>
        </Tooltip>
        <IconButton onClick={() => setExpanded(!expanded)}>
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Collapse in={expanded}>
        {renderNetworkStats()}
        {renderMemoryStats()}
        {renderTimingStats()}
        {renderInteractionStats()}
        {renderErrors()}
      </Collapse>
    </Box>
  );
};

export default PerformanceMonitor; 