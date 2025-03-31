import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Security,
  Warning,
  CheckCircle,
  Error as ErrorIcon,
  Info,
  Visibility,
  Code,
  BugReport,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { MonitoringService } from '../../services/monitoring.service';

interface SecurityVulnerability {
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: string;
  location: string;
  description?: string;
  code_snippet?: string;
  recommendation?: string;
}

interface SecurityTestResults {
  success: boolean;
  vulnerabilities: SecurityVulnerability[];
  passed_checks: number;
  total_checks: number;
  scan_duration?: number;
  timestamp?: string;
}

interface SecurityTestDashboardProps {
  results: SecurityTestResults;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
}));

const MetricBox = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.default,
}));

const getSeverityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return '#d32f2f';
    case 'high':
      return '#f44336';
    case 'medium':
      return '#ff9800';
    case 'low':
      return '#4caf50';
    default:
      return '#757575';
  }
};

const getSeverityIcon = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
    case 'high':
      return <ErrorIcon />;
    case 'medium':
      return <Warning />;
    case 'low':
      return <Info />;
    default:
      return <BugReport />;
  }
};

export const SecurityTestDashboard: React.FC<SecurityTestDashboardProps> = ({ results }) => {
  const [selectedVulnerability, setSelectedVulnerability] = useState<SecurityVulnerability | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  
  const monitoring = MonitoringService.getInstance();

  useEffect(() => {
    monitoring.recordMetric({
      category: 'security_test',
      name: 'dashboard_loaded',
      value: 1,
      tags: {
        vulnerabilities: results.vulnerabilities.length,
        pass_rate: (results.passed_checks / results.total_checks) * 100
      }
    });
  }, [results]);

  const handleVulnerabilityClick = (vulnerability: SecurityVulnerability) => {
    setSelectedVulnerability(vulnerability);
    setDialogOpen(true);

    monitoring.recordMetric({
      category: 'security_test',
      name: 'vulnerability_viewed',
      value: 1,
      tags: {
        severity: vulnerability.severity,
        type: vulnerability.type
      }
    });
  };

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    try {
      // Mock report generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const reportData = {
        ...results,
        generated_at: new Date().toISOString(),
        summary: {
          total_vulnerabilities: results.vulnerabilities.length,
          by_severity: results.vulnerabilities.reduce((acc, v) => ({
            ...acc,
            [v.severity]: (acc[v.severity] || 0) + 1
          }), {} as Record<string, number>)
        }
      };

      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `security-report-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      monitoring.recordMetric({
        category: 'security_test',
        name: 'report_generated',
        value: 1
      });
    } catch (error) {
      monitoring.recordError('generate_report_failed', error);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const renderVulnerabilityDialog = () => {
    if (!selectedVulnerability) return null;

    return (
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getSeverityIcon(selectedVulnerability.severity)}
            <Typography variant="h6">
              {selectedVulnerability.type}
            </Typography>
            <Chip
              label={selectedVulnerability.severity.toUpperCase()}
              size="small"
              sx={{
                backgroundColor: getSeverityColor(selectedVulnerability.severity),
                color: 'white',
                ml: 'auto'
              }}
            />
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            Location
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {selectedVulnerability.location}
          </Typography>

          {selectedVulnerability.description && (
            <>
              <Typography variant="subtitle1" gutterBottom>
                Description
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {selectedVulnerability.description}
              </Typography>
            </>
          )}

          {selectedVulnerability.code_snippet && (
            <>
              <Typography variant="subtitle1" gutterBottom>
                Vulnerable Code
              </Typography>
              <SyntaxHighlighter
                language="typescript"
                style={tomorrow}
                customStyle={{ borderRadius: 4 }}
              >
                {selectedVulnerability.code_snippet}
              </SyntaxHighlighter>
            </>
          )}

          {selectedVulnerability.recommendation && (
            <>
              <Typography variant="subtitle1" gutterBottom>
                Recommendation
              </Typography>
              <Typography variant="body2">
                {selectedVulnerability.recommendation}
              </Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">Security Test Results</Typography>
        <Button
          variant="contained"
          startIcon={isGeneratingReport ? <CircularProgress size={20} /> : <Security />}
          onClick={handleGenerateReport}
          disabled={isGeneratingReport}
        >
          Generate Report
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Summary Metrics */}
        <Grid item xs={12} md={3}>
          <StyledPaper>
            <MetricBox>
              <Typography variant="h4" color="primary">
                {results.passed_checks}/{results.total_checks}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Checks Passed
              </Typography>
              <Box sx={{ mt: 1 }}>
                <CircularProgress
                  variant="determinate"
                  value={(results.passed_checks / results.total_checks) * 100}
                  sx={{
                    color: (results.passed_checks / results.total_checks) >= 0.8
                      ? '#4caf50'
                      : '#f44336'
                  }}
                />
              </Box>
            </MetricBox>
          </StyledPaper>
        </Grid>

        {/* Vulnerabilities by Severity */}
        <Grid item xs={12} md={9}>
          <StyledPaper>
            <Typography variant="subtitle1" gutterBottom>
              Vulnerabilities by Severity
            </Typography>
            <Grid container spacing={2}>
              {['critical', 'high', 'medium', 'low'].map(severity => (
                <Grid item xs={3} key={severity}>
                  <MetricBox>
                    <Typography
                      variant="h4"
                      sx={{ color: getSeverityColor(severity) }}
                    >
                      {results.vulnerabilities.filter(v => v.severity === severity).length}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {severity.charAt(0).toUpperCase() + severity.slice(1)}
                    </Typography>
                  </MetricBox>
                </Grid>
              ))}
            </Grid>
          </StyledPaper>
        </Grid>

        {/* Vulnerabilities Table */}
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="subtitle1" gutterBottom>
              Detected Vulnerabilities
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Severity</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.vulnerabilities.map((vulnerability, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getSeverityIcon(vulnerability.severity)}
                          <Chip
                            label={vulnerability.severity.toUpperCase()}
                            size="small"
                            sx={{
                              backgroundColor: getSeverityColor(vulnerability.severity),
                              color: 'white'
                            }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>{vulnerability.type}</TableCell>
                      <TableCell>{vulnerability.location}</TableCell>
                      <TableCell align="right">
                        <IconButton
                          onClick={() => handleVulnerabilityClick(vulnerability)}
                        >
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </StyledPaper>
        </Grid>
      </Grid>

      {renderVulnerabilityDialog()}
    </Box>
  );
};
