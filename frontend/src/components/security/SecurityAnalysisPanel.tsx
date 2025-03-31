import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Divider,
  Button,
  TextField,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import {
  Security as SecurityIcon,
  BugReport as VulnerabilityIcon,
  Warning as WarningIcon,
  CheckCircle as SecureIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Lock as LockIcon,
  Shield as ShieldIcon,
  Gavel as ComplianceIcon
} from '@mui/icons-material';

interface SecurityIssue {
  id: string;
  type: 'vulnerability' | 'warning' | 'info';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  file: string;
  line: number;
  fix?: string;
  references?: string[];
}

interface SecurityScan {
  id: string;
  timestamp: Date;
  issues: SecurityIssue[];
  summary: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    secure: number;
  };
}

interface ComplianceCheck {
  id: string;
  standard: string;
  status: 'compliant' | 'partial' | 'non-compliant';
  issues: string[];
  recommendations: string[];
}

interface SecurityAnalysisPanelProps {
  onScan: () => void;
  onFixIssue: (issueId: string) => void;
  onViewDetails: (issueId: string) => void;
}

const SecurityAnalysisPanel: React.FC<SecurityAnalysisPanelProps> = ({
  onScan,
  onFixIssue,
  onViewDetails
}) => {
  const [isScanning, setIsScanning] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<SecurityIssue | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [securityScan, setSecurityScan] = useState<SecurityScan | null>(null);
  const [complianceChecks, setComplianceChecks] = useState<ComplianceCheck[]>([]);

  const handleScan = async () => {
    setIsScanning(true);
    try {
      await onScan();
      // Simulate scan results
      setSecurityScan({
        id: Date.now().toString(),
        timestamp: new Date(),
        issues: [
          {
            id: '1',
            type: 'vulnerability',
            severity: 'high',
            title: 'SQL Injection Vulnerability',
            description: 'Potential SQL injection vulnerability in database query',
            file: 'src/database/queries.ts',
            line: 45,
            fix: 'Use parameterized queries instead of string concatenation',
            references: ['https://owasp.org/www-project-top-ten/2017/A1_2017-Injection']
          },
          {
            id: '2',
            type: 'warning',
            severity: 'medium',
            title: 'Weak Password Policy',
            description: 'Password requirements do not meet security standards',
            file: 'src/auth/password.ts',
            line: 12,
            fix: 'Implement stronger password requirements',
            references: ['https://owasp.org/www-project-cheat-sheets/cheatsheets/Password_Storage_Cheat_Sheet.html']
          }
        ],
        summary: {
          total: 2,
          critical: 0,
          high: 1,
          medium: 1,
          low: 0,
          secure: 0
        }
      });

      setComplianceChecks([
        {
          id: '1',
          standard: 'OWASP Top 10',
          status: 'partial',
          issues: ['SQL Injection vulnerability detected'],
          recommendations: ['Implement input validation', 'Use parameterized queries']
        },
        {
          id: '2',
          standard: 'GDPR',
          status: 'compliant',
          issues: [],
          recommendations: []
        }
      ]);
    } finally {
      setIsScanning(false);
    }
  };

  const handleFixIssue = async (issueId: string) => {
    await onFixIssue(issueId);
    setSecurityScan(prev => prev ? {
      ...prev,
      issues: prev.issues.filter(issue => issue.id !== issueId)
    } : null);
  };

  const handleViewDetails = (issue: SecurityIssue) => {
    setSelectedIssue(issue);
  };

  const handleCloseDetails = () => {
    setSelectedIssue(null);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 1 }}>
        <SecurityIcon color="primary" />
        <Typography variant="h6" sx={{ flex: 1 }}>Security Analysis</Typography>
        <Tooltip title="Run Security Scan">
          <IconButton onClick={handleScan} disabled={isScanning}>
            {isScanning ? <CircularProgress size={24} /> : <RefreshIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {securityScan && (
          <>
            <Box sx={{ p: 2, bgcolor: 'background.default' }}>
              <Typography variant="subtitle1" gutterBottom>Scan Summary</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="h6" color="error">
                      {securityScan.summary.critical + securityScan.summary.high}
                    </Typography>
                    <Typography variant="body2">High/Critical Issues</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="h6" color="warning.main">
                      {securityScan.summary.medium}
                    </Typography>
                    <Typography variant="body2">Medium Issues</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="h6" color="info.main">
                      {securityScan.summary.low}
                    </Typography>
                    <Typography variant="body2">Low Issues</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="h6" color="success.main">
                      {securityScan.summary.secure}
                    </Typography>
                    <Typography variant="body2">Secure</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>

            <Divider />

            <List>
              <ListItem>
                <ListItemIcon>
                  <VulnerabilityIcon />
                </ListItemIcon>
                <ListItemText primary="Security Issues" />
              </ListItem>
              {securityScan.issues.map(issue => (
                <ListItem
                  key={issue.id}
                  secondaryAction={
                    <Box>
                      <Tooltip title="View Details">
                        <IconButton edge="end" onClick={() => handleViewDetails(issue)}>
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Fix Issue">
                        <IconButton edge="end" onClick={() => handleFixIssue(issue.id)}>
                          <SecureIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                >
                  <ListItemIcon>
                    {issue.type === 'vulnerability' ? <VulnerabilityIcon color="error" /> :
                     issue.type === 'warning' ? <WarningIcon color="warning" /> :
                     <InfoIcon color="info" />}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {issue.title}
                        <Chip
                          size="small"
                          label={issue.severity}
                          color={getSeverityColor(issue.severity)}
                        />
                      </Box>
                    }
                    secondary={`${issue.file}:${issue.line}`}
                  />
                </ListItem>
              ))}
            </List>

            <Divider />

            <List>
              <ListItem>
                <ListItemIcon>
                  <ComplianceIcon />
                </ListItemIcon>
                <ListItemText primary="Compliance Checks" />
              </ListItem>
              {complianceChecks.map(check => (
                <ListItem
                  key={check.id}
                  secondaryAction={
                    <Chip
                      label={check.status}
                      color={
                        check.status === 'compliant' ? 'success' :
                        check.status === 'partial' ? 'warning' :
                        'error'
                      }
                    />
                  }
                >
                  <ListItemText
                    primary={check.standard}
                    secondary={check.issues.length > 0 ? check.issues.join(', ') : 'No issues found'}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </Box>

      <Dialog
        open={Boolean(selectedIssue)}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {selectedIssue?.type === 'vulnerability' ? <VulnerabilityIcon color="error" /> :
             selectedIssue?.type === 'warning' ? <WarningIcon color="warning" /> :
             <InfoIcon color="info" />}
            {selectedIssue?.title}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Description</Typography>
            <Typography paragraph>{selectedIssue?.description}</Typography>

            <Typography variant="subtitle1" gutterBottom>Location</Typography>
            <Typography paragraph>{selectedIssue?.file}:{selectedIssue?.line}</Typography>

            {selectedIssue?.fix && (
              <>
                <Typography variant="subtitle1" gutterBottom>Suggested Fix</Typography>
                <Typography paragraph>{selectedIssue?.fix}</Typography>
              </>
            )}

            {selectedIssue?.references && selectedIssue.references.length > 0 && (
              <>
                <Typography variant="subtitle1" gutterBottom>References</Typography>
                <List>
                  {selectedIssue.references.map((ref, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={ref} />
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
          {selectedIssue && (
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleFixIssue(selectedIssue.id)}
            >
              Apply Fix
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default SecurityAnalysisPanel; 