import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Collapse,
  Button,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  ExpandMore as ExpandMoreIcon,
  Build as AutoFixIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
} from '@mui/icons-material';
import { CodeQualityService, CodeIssue, FileAnalysis } from '../../services/codeAnalysis/CodeQualityService';

const ReviewPanel = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
}));

const ScrollableContent = styled(Box)({
  flex: 1,
  overflow: 'auto',
  padding: '16px',
});

const MetricsContainer = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
  gap: theme.spacing(2),
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const MetricCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'center',
  backgroundColor: theme.palette.background.default,
}));

interface AIReviewPanelProps {
  filePath: string;
  onFixApply: (fix: CodeIssue['fix']) => void;
  onNavigateToIssue: (line: number, column: number) => void;
}

const severityIcons = {
  error: <ErrorIcon color="error" />,
  warning: <WarningIcon color="warning" />,
  info: <InfoIcon color="info" />,
  suggestion: <SuccessIcon color="success" />,
};

const AIReviewPanel: React.FC<AIReviewPanelProps> = ({
  filePath,
  onFixApply,
  onNavigateToIssue,
}) => {
  const [analysis, setAnalysis] = useState<FileAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedIssue, setExpandedIssue] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const codeQualityService = CodeQualityService.getInstance();
    
    // Subscribe to analysis updates
    const unsubscribe = codeQualityService.subscribeToAnalysis(
      filePath,
      (newAnalysis) => {
        setAnalysis(newAnalysis);
        setLoading(false);
      }
    );

    // Get initial analysis from cache or trigger new analysis
    const cachedAnalysis = codeQualityService.getCachedAnalysis(filePath);
    if (cachedAnalysis) {
      setAnalysis(cachedAnalysis);
      setLoading(false);
    }

    return () => {
      unsubscribe();
    };
  }, [filePath]);

  const handleFeedback = async (issueId: string, isHelpful: boolean) => {
    setFeedback(prev => ({
      ...prev,
      [issueId]: isHelpful,
    }));

    // Send feedback to API
    try {
      await fetch('/api/code-review/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          issueId,
          isHelpful,
          filePath,
        }),
      });
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  };

  const renderMetrics = () => {
    if (!analysis?.metrics) return null;

    return (
      <MetricsContainer>
        {Object.entries(analysis.metrics).map(([key, value]) => (
          <MetricCard key={key} elevation={0}>
            <Typography variant="h6" color="primary">
              {Math.round(value * 100)}%
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </Typography>
          </MetricCard>
        ))}
      </MetricsContainer>
    );
  };

  const renderIssue = (issue: CodeIssue) => {
    const isExpanded = expandedIssue === issue.id;
    const hasUserFeedback = feedback[issue.id] !== undefined;

    return (
      <ListItem
        key={issue.id}
        sx={{
          flexDirection: 'column',
          alignItems: 'flex-start',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Box
          sx={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
          }}
          onClick={() => setExpandedIssue(isExpanded ? null : issue.id)}
        >
          <ListItemIcon>{severityIcons[issue.type]}</ListItemIcon>
          <ListItemText
            primary={issue.message}
            secondary={`Line ${issue.line}, Column ${issue.column}`}
          />
          <Box>
            <Chip
              size="small"
              label={issue.rule}
              sx={{ mr: 1 }}
            />
            <IconButton size="small">
              <ExpandMoreIcon
                sx={{
                  transform: isExpanded ? 'rotate(180deg)' : 'none',
                  transition: '0.2s',
                }}
              />
            </IconButton>
          </Box>
        </Box>

        <Collapse in={isExpanded} sx={{ width: '100%' }}>
          <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1, my: 1 }}>
            {issue.fix && (
              <Button
                startIcon={<AutoFixIcon />}
                variant="outlined"
                size="small"
                sx={{ mb: 2 }}
                onClick={() => onFixApply(issue.fix!)}
              >
                Apply Fix
              </Button>
            )}
            
            <Typography variant="body2" sx={{ mb: 2 }}>
              {issue.description}
            </Typography>

            {!hasUserFeedback && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="Helpful">
                  <IconButton
                    size="small"
                    onClick={() => handleFeedback(issue.id, true)}
                  >
                    <ThumbUpIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Not Helpful">
                  <IconButton
                    size="small"
                    onClick={() => handleFeedback(issue.id, false)}
                  >
                    <ThumbDownIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            )}
          </Box>
        </Collapse>
      </ListItem>
    );
  };

  if (loading) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height="100%"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ReviewPanel>
      {renderMetrics()}
      
      <ScrollableContent>
        {analysis?.issues.length === 0 ? (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            p={4}
          >
            <Typography color="success.main" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SuccessIcon />
              No issues found
            </Typography>
          </Box>
        ) : (
          <List>
            {analysis?.issues.map(renderIssue)}
          </List>
        )}

        {Boolean(analysis?.aiInsights?.length) && (
          <Box mt={4}>
            <Typography variant="h6" gutterBottom>
              AI Insights
            </Typography>
            <List>
              {analysis?.aiInsights?.map((insight, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <InfoIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={insight} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </ScrollableContent>
    </ReviewPanel>
  );
};

export default AIReviewPanel;