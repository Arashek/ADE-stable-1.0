import React, { useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Collapse,
  useTheme,
  Tooltip,
  Divider
} from '@mui/material';
import {
  Check as CheckIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ErrorOutline as ErrorIcon,
  Warning as WarningIcon,
  Lightbulb as IdeaIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { CodeContext, AISuggestion } from '../../types/visualization.types';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark, materialLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeInsightProps {
  code: string;
  context: CodeContext;
  suggestions: AISuggestion[];
  onApply: (suggestion: AISuggestion) => void;
}

const getSuggestionIcon = (type: AISuggestion['type']) => {
  switch (type) {
    case 'error':
      return <ErrorIcon color="error" />;
    case 'warning':
      return <WarningIcon color="warning" />;
    case 'improvement':
      return <IdeaIcon color="info" />;
    case 'optimization':
      return <SpeedIcon color="success" />;
    default:
      return <IdeaIcon />;
  }
};

const getSuggestionBorderColor = (type: AISuggestion['type'], theme: any) => {
  if (type === 'error') {
    return theme.palette.error.main;
  }
  return theme.palette.divider;
};

const CodeInsight: React.FC<CodeInsightProps> = ({
  code,
  context,
  suggestions,
  onApply
}) => {
  const theme = useTheme();
  const [expandedSuggestion, setExpandedSuggestion] = React.useState<string | null>(null);

  const handleToggleExpand = (id: string) => {
    setExpandedSuggestion(expandedSuggestion === id ? null : id);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: { xs: 'column', lg: 'row' },
        gap: 2,
        height: '100%'
      }}
    >
      <Paper
        elevation={2}
        sx={{
          flex: 1,
          p: 2,
          borderRadius: 2,
          overflow: 'auto'
        }}
      >
        <Typography variant="h6" gutterBottom>
          Code
        </Typography>
        <Box sx={{ position: 'relative' }}>
          <SyntaxHighlighter
            language={context.language.toLowerCase()}
            style={theme.palette.mode === 'dark' ? materialDark : materialLight}
            customStyle={{
              margin: 0,
              borderRadius: theme.shape.borderRadius,
              maxHeight: '70vh'
            }}
          >
            {code}
          </SyntaxHighlighter>
        </Box>
      </Paper>

      <Paper
        elevation={2}
        sx={{
          flex: 1,
          p: 2,
          borderRadius: 2,
          overflow: 'auto'
        }}
      >
        <Typography variant="h6" gutterBottom>
          AI Suggestions
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {suggestions.map((suggestion) => (
            <Paper
              key={suggestion.id}
              variant="outlined"
              sx={{
                p: 2,
                borderRadius: 2,
                borderColor: getSuggestionBorderColor(suggestion.type, theme)
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                {getSuggestionIcon(suggestion.type)}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1">
                    {suggestion.title}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1, mb: 1 }}>
                    <Chip
                      size="small"
                      label={suggestion.type}
                      color={
                        suggestion.type === 'error' ? 'error' :
                        suggestion.type === 'warning' ? 'warning' :
                        suggestion.type === 'improvement' ? 'info' :
                        'success'
                      }
                    />
                    <Chip
                      size="small"
                      label={suggestion.impact}
                      variant="outlined"
                    />
                    <Chip
                      size="small"
                      label={suggestion.category}
                      variant="outlined"
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {suggestion.description}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {suggestion.code && (
                    <Tooltip title="Expand code">
                      <IconButton
                        size="small"
                        onClick={() => handleToggleExpand(suggestion.id)}
                        sx={{
                          transform: expandedSuggestion === suggestion.id ? 'rotate(180deg)' : 'none',
                          transition: 'transform 0.3s'
                        }}
                      >
                        <ExpandMoreIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Tooltip title="Apply suggestion">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => onApply(suggestion)}
                    >
                      <CheckIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Dismiss">
                    <IconButton size="small">
                      <CloseIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              
              {suggestion.code && (
                <Collapse in={expandedSuggestion === suggestion.id}>
                  <Divider sx={{ my: 2 }} />
                  <SyntaxHighlighter
                    language={context.language.toLowerCase()}
                    style={theme.palette.mode === 'dark' ? materialDark : materialLight}
                    customStyle={{
                      margin: 0,
                      borderRadius: theme.shape.borderRadius,
                      maxHeight: '200px'
                    }}
                  >
                    {suggestion.code}
                  </SyntaxHighlighter>
                </Collapse>
              )}
            </Paper>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default CodeInsight; 