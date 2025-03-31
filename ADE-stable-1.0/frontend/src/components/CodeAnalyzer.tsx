import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  LinearProgress,
  Tooltip,
  Divider,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Rating
} from '@mui/material';
import {
  Code as CodeIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  BugReport as BugReportIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

interface CodeAnalysis {
  id: string;
  filePath: string;
  fileName: string;
  language: string;
  timestamp: string;
  metrics: {
    complexity: number;
    maintainability: number;
    security: number;
    performance: number;
    reliability: number;
  };
  issues: Array<{
    type: 'security' | 'performance' | 'reliability' | 'maintainability';
    severity: 'critical' | 'high' | 'medium' | 'low';
    description: string;
    lineNumber: number;
    suggestion: string;
  }>;
  aiSuggestions: {
    optimizations: Array<{
      type: string;
      description: string;
      impact: string;
      implementation: string;
    }>;
    securityRecommendations: Array<{
      type: string;
      description: string;
      risk: string;
      mitigation: string;
    }>;
    bestPractices: Array<{
      category: string;
      description: string;
      benefit: string;
    }>;
  };
}

interface CodeAnalyzerProps {
  projectId: string;
}

const CodeAnalyzer: React.FC<CodeAnalyzerProps> = ({ projectId }) => {
  const [analyses, setAnalyses] = useState<CodeAnalysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<CodeAnalysis | null>(null);
  const [newAnalysis, setNewAnalysis] = useState<Partial<CodeAnalysis>>({
    filePath: '',
    fileName: '',
    language: '',
    timestamp: new Date().toISOString(),
    metrics: {
      complexity: 0,
      maintainability: 0,
      security: 0,
      performance: 0,
      reliability: 0
    },
    issues: [],
    aiSuggestions: {
      optimizations: [],
      securityRecommendations: [],
      bestPractices: []
    }
  });

  useEffect(() => {
    fetchAnalyses();
  }, [projectId]);

  const fetchAnalyses = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/code-analysis?projectId=${projectId}`);
      const data = await response.json();
      setAnalyses(data.analyses);
    } catch (err) {
      setError('Failed to fetch code analyses');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCode = async () => {
    try {
      // First, get AI analysis of the code
      const analysisResponse = await fetch('/api/code-analysis/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filePath: newAnalysis.filePath,
          fileName: newAnalysis.fileName,
          language: newAnalysis.language
        }),
      });
      const analysis = await analysisResponse.json();

      // Create analysis with AI insights
      const response = await fetch('/api/code-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newAnalysis,
          projectId,
          aiSuggestions: analysis
        }),
      });

      if (response.ok) {
        const createdAnalysis = await response.json();
        setAnalyses(prev => [...prev, createdAnalysis]);
        setOpenDialog(false);
        setNewAnalysis({
          filePath: '',
          fileName: '',
          language: '',
          timestamp: new Date().toISOString(),
          metrics: {
            complexity: 0,
            maintainability: 0,
            security: 0,
            performance: 0,
            reliability: 0
          },
          issues: [],
          aiSuggestions: {
            optimizations: [],
            securityRecommendations: [],
            bestPractices: []
          }
        });
      } else {
        throw new Error('Failed to create analysis');
      }
    } catch (err) {
      setError('Failed to create analysis');
    }
  };

  const handleOptimizeCode = async (analysisId: string) => {
    try {
      const response = await fetch(`/api/code-analysis/${analysisId}/optimize`, {
        method: 'POST',
      });
      if (response.ok) {
        const optimization = await response.json();
        setAnalyses(prev => prev.map(analysis => 
          analysis.id === analysisId 
            ? { ...analysis, aiSuggestions: { ...analysis.aiSuggestions, optimizations: optimization.suggestions } }
            : analysis
        ));
      } else {
        throw new Error('Failed to optimize code');
      }
    } catch (err) {
      setError('Failed to optimize code');
    }
  };

  const handleSecurityCheck = async (analysisId: string) => {
    try {
      const response = await fetch(`/api/code-analysis/${analysisId}/security`, {
        method: 'POST',
      });
      if (response.ok) {
        const security = await response.json();
        setAnalyses(prev => prev.map(analysis => 
          analysis.id === analysisId 
            ? { ...analysis, aiSuggestions: { ...analysis.aiSuggestions, securityRecommendations: security.recommendations } }
            : analysis
        ));
      } else {
        throw new Error('Failed to perform security check');
      }
    } catch (err) {
      setError('Failed to perform security check');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getMetricColor = (value: number) => {
    if (value >= 80) return 'success';
    if (value >= 60) return 'warning';
    return 'error';
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Code Analysis & Optimization</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              New Analysis
            </Button>
          </Box>
        </Grid>

        {/* Error Alert */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}

        {/* Analysis List */}
        <Grid item xs={12}>
          <Paper>
            <List>
              {analyses.map((analysis) => (
                <React.Fragment key={analysis.id}>
                  <ListItem>
                    <ListItemIcon>
                      <CodeIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {analysis.fileName}
                          <Chip
                            size="small"
                            label={analysis.language}
                            icon={<CodeIcon />}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {analysis.filePath}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip
                              size="small"
                              label={`Complexity: ${analysis.metrics.complexity}`}
                              color={getMetricColor(100 - analysis.metrics.complexity)}
                              icon={<AssessmentIcon />}
                            />
                            <Chip
                              size="small"
                              label={`Security: ${analysis.metrics.security}`}
                              color={getMetricColor(analysis.metrics.security)}
                              icon={<SecurityIcon />}
                            />
                            <Chip
                              size="small"
                              label={`Performance: ${analysis.metrics.performance}`}
                              color={getMetricColor(analysis.metrics.performance)}
                              icon={<SpeedIcon />}
                            />
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Optimize Code">
                        <IconButton
                          edge="end"
                          onClick={() => handleOptimizeCode(analysis.id)}
                          sx={{ mr: 1 }}
                        >
                          <SpeedIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Security Check">
                        <IconButton
                          edge="end"
                          onClick={() => handleSecurityCheck(analysis.id)}
                          sx={{ mr: 1 }}
                        >
                          <SecurityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Analysis">
                        <IconButton
                          edge="end"
                          onClick={() => {
                            setSelectedAnalysis(analysis);
                            setOpenDialog(true);
                          }}
                          sx={{ mr: 1 }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Analysis">
                        <IconButton
                          edge="end"
                          onClick={() => {
                            // Implement delete functionality
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>

                  {/* Issues */}
                  {analysis.issues.length > 0 && (
                    <Card sx={{ ml: 4, mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Issues Found
                        </Typography>
                        <List>
                          {analysis.issues.map((issue, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                {issue.type === 'security' ? <SecurityIcon color="error" /> :
                                 issue.type === 'performance' ? <SpeedIcon color="warning" /> :
                                 issue.type === 'reliability' ? <BugReportIcon color="error" /> :
                                 <WarningIcon color="warning" />}
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    {issue.description}
                                    <Chip
                                      size="small"
                                      label={issue.severity}
                                      color={getSeverityColor(issue.severity)}
                                    />
                                  </Box>
                                }
                                secondary={
                                  <Box>
                                    <Typography variant="body2">
                                      Line {issue.lineNumber}
                                    </Typography>
                                    <Typography variant="body2" color="primary">
                                      Suggestion: {issue.suggestion}
                                    </Typography>
                                  </Box>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  )}

                  {/* AI Suggestions */}
                  {analysis.aiSuggestions && (
                    <Card sx={{ ml: 4, mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          AI Suggestions
                        </Typography>
                        <Grid container spacing={2}>
                          {/* Optimizations */}
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Optimizations
                            </Typography>
                            <List>
                              {analysis.aiSuggestions.optimizations.map((opt, index) => (
                                <ListItem key={index}>
                                  <ListItemIcon>
                                    <SpeedIcon />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={opt.description}
                                    secondary={
                                      <Box>
                                        <Typography variant="body2">
                                          Impact: {opt.impact}
                                        </Typography>
                                        <Typography variant="body2" color="primary">
                                          Implementation: {opt.implementation}
                                        </Typography>
                                      </Box>
                                    }
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Grid>

                          {/* Security Recommendations */}
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Security Recommendations
                            </Typography>
                            <List>
                              {analysis.aiSuggestions.securityRecommendations.map((rec, index) => (
                                <ListItem key={index}>
                                  <ListItemIcon>
                                    <SecurityIcon />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={rec.description}
                                    secondary={
                                      <Box>
                                        <Typography variant="body2">
                                          Risk: {rec.risk}
                                        </Typography>
                                        <Typography variant="body2" color="primary">
                                          Mitigation: {rec.mitigation}
                                        </Typography>
                                      </Box>
                                    }
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Grid>

                          {/* Best Practices */}
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Best Practices
                            </Typography>
                            <List>
                              {analysis.aiSuggestions.bestPractices.map((practice, index) => (
                                <ListItem key={index}>
                                  <ListItemIcon>
                                    <CheckCircleIcon />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={practice.description}
                                    secondary={
                                      <Box>
                                        <Typography variant="body2">
                                          Category: {practice.category}
                                        </Typography>
                                        <Typography variant="body2" color="primary">
                                          Benefit: {practice.benefit}
                                        </Typography>
                                      </Box>
                                    }
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  )}
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Analysis Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedAnalysis ? 'Edit Analysis' : 'New Code Analysis'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="File Path"
                value={newAnalysis.filePath}
                onChange={(e) => setNewAnalysis({ ...newAnalysis, filePath: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="File Name"
                value={newAnalysis.fileName}
                onChange={(e) => setNewAnalysis({ ...newAnalysis, fileName: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={newAnalysis.language}
                  label="Language"
                  onChange={(e) => setNewAnalysis({ ...newAnalysis, language: e.target.value })}
                >
                  <MenuItem value="typescript">TypeScript</MenuItem>
                  <MenuItem value="javascript">JavaScript</MenuItem>
                  <MenuItem value="python">Python</MenuItem>
                  <MenuItem value="java">Java</MenuItem>
                  <MenuItem value="cpp">C++</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAnalyzeCode} variant="contained" color="primary">
            {selectedAnalysis ? 'Save Changes' : 'Analyze Code'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CodeAnalyzer; 