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
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Download as DownloadIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import { DocumentationResponse } from '../../types/agent.types';

interface DocumentationResultsProps {
  result: DocumentationResponse;
  onDownload: (id: string) => Promise<void>;
}

export const DocumentationResults: React.FC<DocumentationResultsProps> = ({
  result,
  onDownload,
}) => {
  const [tabValue, setTabValue] = React.useState(0);
  const [expandedExamples, setExpandedExamples] = React.useState<Set<number>>(new Set());

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const toggleExample = (index: number) => {
    const newExpanded = new Set(expandedExamples);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedExamples(newExpanded);
  };

  const renderContent = () => {
    if (result.format === 'markdown') {
      return (
        <ReactMarkdown
          components={{
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {result.content}
        </ReactMarkdown>
      );
    }
    return (
      <Typography
        component="div"
        sx={{
          '& pre': {
            bgcolor: 'background.paper',
            p: 2,
            borderRadius: 1,
            overflow: 'auto',
          },
        }}
      >
        {result.content}
      </Typography>
    );
  };

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Documentation</Typography>
        <Tooltip title="Download Documentation">
          <IconButton onClick={() => onDownload(result.id)} color="primary">
            <DownloadIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box mb={2}>
            {result.doc_types.map((type) => (
              <Chip
                key={type}
                label={type}
                color="primary"
                size="small"
                sx={{ mr: 1 }}
              />
            ))}
            <Chip
              label={result.format}
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
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab
                icon={<DescriptionIcon />}
                label="Content"
                id="doc-tab-0"
                aria-controls="doc-tabpanel-0"
              />
              {result.examples && result.examples.length > 0 && (
                <Tab
                  icon={<CodeIcon />}
                  label="Examples"
                  id="doc-tab-1"
                  aria-controls="doc-tabpanel-1"
                />
              )}
            </Tabs>
          </Box>

          <Box role="tabpanel" hidden={tabValue !== 0} sx={{ mt: 2 }}>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
              {renderContent()}
            </Paper>
          </Box>

          {result.examples && result.examples.length > 0 && (
            <Box role="tabpanel" hidden={tabValue !== 1} sx={{ mt: 2 }}>
              {result.examples.map((example, index) => (
                <Accordion
                  key={index}
                  expanded={expandedExamples.has(index)}
                  onChange={() => toggleExample(index)}
                  sx={{ mb: 1 }}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Example {index + 1}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                      <SyntaxHighlighter
                        language="typescript"
                        style={vscDarkPlus}
                        customStyle={{ margin: 0, borderRadius: 4 }}
                      >
                        {example}
                      </SyntaxHighlighter>
                    </Paper>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom>
            Documentation Details
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip
              label={`Format: ${result.format}`}
              variant="outlined"
              size="small"
            />
            <Chip
              label={`Style: ${result.style}`}
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