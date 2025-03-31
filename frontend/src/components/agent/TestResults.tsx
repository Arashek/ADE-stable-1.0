import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Divider,
  IconButton,
  Tooltip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Download as DownloadIcon,
  ExpandMore as ExpandMoreIcon,
  BugReport as BugReportIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { TestGenerationResponse } from '../../types/agent.types';

interface TestResultsProps {
  result: TestGenerationResponse;
  onDownload: (id: string) => Promise<void>;
}

export const TestResults: React.FC<TestResultsProps> = ({ result, onDownload }) => {
  const [expandedTests, setExpandedTests] = React.useState<Set<number>>(new Set());

  const toggleTest = (index: number) => {
    const newExpanded = new Set(expandedTests);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedTests(newExpanded);
  };

  const getCoverageColor = (percentage: number) => {
    if (percentage >= 90) return 'success';
    if (percentage >= 70) return 'warning';
    return 'error';
  };

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Test Suite Results</Typography>
        <Tooltip title="Download Test Suite">
          <IconButton onClick={() => onDownload(result.id)} color="primary">
            <DownloadIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box mb={2}>
            {result.test_types.map((type) => (
              <Chip
                key={type}
                label={type}
                color="primary"
                size="small"
                sx={{ mr: 1 }}
              />
            ))}
            <Chip
              label={result.framework}
              color="secondary"
              size="small"
              sx={{ mr: 1 }}
            />
            <Chip
              label={`Generated: ${new Date(result.timestamp).toLocaleString()}`}
              variant="outlined"
              size="small"
            />
          </Box>

          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Coverage Report
            </Typography>
            <Box display="flex" alignItems="center" mb={1}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {result.coverage_report.coverage_percentage}% Coverage
              </Typography>
              <Box flexGrow={1}>
                <LinearProgress
                  variant="determinate"
                  value={result.coverage_report.coverage_percentage}
                  color={getCoverageColor(result.coverage_report.coverage_percentage)}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {result.coverage_report.covered_lines} of {result.coverage_report.total_lines} lines covered
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Test Cases
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
            <SyntaxHighlighter
              language="typescript"
              style={vscDarkPlus}
              customStyle={{ margin: 0, borderRadius: 4 }}
            >
              {result.test_suite}
            </SyntaxHighlighter>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom>
            Test Details
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip
              label={`File: ${result.file_path}`}
              variant="outlined"
              size="small"
            />
            <Chip
              label={`Framework: ${result.framework}`}
              variant="outlined"
              size="small"
            />
            <Chip
              label={`Generated: ${new Date(result.timestamp).toLocaleString()}`}
              variant="outlined"
              size="small"
            />
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}; 