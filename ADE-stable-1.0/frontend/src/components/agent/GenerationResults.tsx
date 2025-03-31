import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  Chip,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CodeGenerationResponse } from '../../types/agent.types';

interface GenerationResultsProps {
  result: CodeGenerationResponse;
  onDownload: (id: string) => Promise<void>;
}

export const GenerationResults: React.FC<GenerationResultsProps> = ({
  result,
  onDownload,
}) => {
  const handleDownload = async () => {
    await onDownload(result.id);
  };

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Generated Code</Typography>
        <Tooltip title="Download Code">
          <IconButton onClick={handleDownload} color="primary">
            <DownloadIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box mb={2}>
            <Chip
              label={result.language}
              color="primary"
              size="small"
              sx={{ mr: 1 }}
            />
            {result.framework && (
              <Chip
                label={result.framework}
                color="secondary"
                size="small"
                sx={{ mr: 1 }}
              />
            )}
            <Chip
              label={`Generated: ${new Date(result.metadata.timestamp).toLocaleString()}`}
              variant="outlined"
              size="small"
            />
          </Box>

          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
            <SyntaxHighlighter
              language={result.language.toLowerCase()}
              style={vscDarkPlus}
              customStyle={{ margin: 0, borderRadius: 4 }}
            >
              {result.generated_code}
            </SyntaxHighlighter>
          </Paper>
        </Grid>

        {result.tests && (
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Box display="flex" alignItems="center" mb={2}>
              <BugReportIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Generated Tests</Typography>
            </Box>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
              <SyntaxHighlighter
                language={result.language.toLowerCase()}
                style={vscDarkPlus}
                customStyle={{ margin: 0, borderRadius: 4 }}
              >
                {result.tests}
              </SyntaxHighlighter>
            </Paper>
          </Grid>
        )}

        {result.documentation && (
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Box display="flex" alignItems="center" mb={2}>
              <DescriptionIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Generated Documentation</Typography>
            </Box>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
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
                {result.documentation}
              </Typography>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
}; 