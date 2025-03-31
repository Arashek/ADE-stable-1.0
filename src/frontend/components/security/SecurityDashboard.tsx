import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Security,
  CheckCircle,
  Error,
  Warning,
  Info,
  Shield,
  Lock,
  NetworkCheck,
  Storage,
  Speed,
} from '@mui/icons-material';
import { SecurityPolicyValidator, ComplianceResult } from '../../../core/models/project/SecurityPolicyValidator';
import { SecurityEvent, SecurityEventType } from '../../../core/models/project/SecurityAuditLogger';
import { SecurityPolicy } from '../../../core/models/project/SecurityManager';

interface SecurityDashboardProps {
  containerId: string;
  containerName: string;
  policy: SecurityPolicy;
  events: SecurityEvent[];
}

const severityColors = {
  critical: 'error',
  high: 'error',
  medium: 'warning',
  low: 'info',
} as const;

const severityIcons = {
  critical: <Error color="error" />,
  high: <Error color="error" />,
  medium: <Warning color="warning" />,
  low: <Info color="info" />,
} as const;

export const SecurityDashboard: React.FC<SecurityDashboardProps> = ({
  containerId,
  containerName,
  policy,
  events,
}) => {
  const [complianceResults, setComplianceResults] = useState<ComplianceResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const validator = new SecurityPolicyValidator();

  useEffect(() => {
    try {
      const results = validator.validatePolicy(policy);
      setComplianceResults(results);
    } catch (err) {
      setError('Failed to validate security policy');
      console.error('Policy validation error:', err);
    } finally {
      setLoading(false);
    }
  }, [policy]);

  const getComplianceSummary = () => {
    const total = complianceResults.length;
    const passed = complianceResults.filter(r => r.passed).length;
    const critical = complianceResults.filter(r => r.severity === 'critical').length;
    const criticalPassed = complianceResults.filter(r => r.severity === 'critical' && r.passed).length;

    return {
      total,
      passed,
      critical,
      criticalPassed,
      percentage: (passed / total) * 100,
    };
  };

  const getRecentSecurityEvents = () => {
    return events
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 5);
  };

  const getSecurityScore = () => {
    const weights = {
      critical: 40,
      high: 30,
      medium: 20,
      low: 10,
    };

    let totalWeight = 0;
    let weightedScore = 0;

    complianceResults.forEach(result => {
      const weight = weights[result.severity];
      totalWeight += weight;
      weightedScore += result.passed ? weight : 0;
    });

    return Math.round((weightedScore / totalWeight) * 100);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  const summary = getComplianceSummary();
  const recentEvents = getRecentSecurityEvents();
  const securityScore = getSecurityScore();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Security Dashboard - {containerName}
      </Typography>

      <Grid container spacing={3}>
        {/* Security Score */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Shield sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6">Security Score</Typography>
                  <Typography variant="h3" color="primary">
                    {securityScore}%
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Based on compliance checks and security events
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Summary */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Compliance Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4">{summary.passed}</Typography>
                    <Typography variant="body2">Passed</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="error">
                      {summary.total - summary.passed}
                    </Typography>
                    <Typography variant="body2">Failed</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="error">
                      {summary.critical - summary.criticalPassed}
                    </Typography>
                    <Typography variant="body2">Critical Failed</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4">
                      {Math.round(summary.percentage)}%
                    </Typography>
                    <Typography variant="body2">Compliance Rate</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Details */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Compliance Details" />
            <CardContent>
              <List>
                {complianceResults.map((result) => (
                  <React.Fragment key={result.ruleId}>
                    <ListItem>
                      <ListItemIcon>
                        {result.passed ? (
                          <CheckCircle color="success" />
                        ) : (
                          severityIcons[result.severity]
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={result.details}
                        secondary={
                          <Box display="flex" alignItems="center" mt={1}>
                            <Chip
                              label={result.severity}
                              color={severityColors[result.severity]}
                              size="small"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {result.ruleId}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Security Events */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recent Security Events" />
            <CardContent>
              <List>
                {recentEvents.map((event) => (
                  <React.Fragment key={`${event.timestamp}-${event.eventType}`}>
                    <ListItem>
                      <ListItemIcon>
                        {severityIcons[event.severity]}
                      </ListItemIcon>
                      <ListItemText
                        primary={event.action}
                        secondary={
                          <Box display="flex" alignItems="center" mt={1}>
                            <Chip
                              label={event.eventType}
                              size="small"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {new Date(event.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 