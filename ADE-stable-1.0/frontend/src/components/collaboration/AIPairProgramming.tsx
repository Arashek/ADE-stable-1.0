import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  TextField,
  Button,
  CircularProgress,
  Collapse,
  Tooltip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Lightbulb as SuggestionIcon,
  Code as CodeIcon,
  BugReport as BugIcon,
  Psychology as AIIcon,
  ExpandMore as ExpandMoreIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import { CollaborationService, TextChange } from '../../services/collaboration/CollaborationService';

interface AISuggestion {
  id: string;
  type: 'code' | 'improvement' | 'bug';
  message: string;
  code?: string;
  explanation?: string;
  confidence: number;
  timestamp: number;
}

const AIContainer = styled(Paper)(({ theme }) => ({
  position: 'fixed',
  bottom: theme.spacing(2),
  right: theme.spacing(32), // Position next to collaboration panel
  width: '400px',
  maxHeight: '600px',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[6],
  zIndex: 1000,
  display: 'flex',
  flexDirection: 'column',
}));

const SuggestionList = styled(List)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(1),
}));

const QueryInput = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${theme.palette.divider}`,
}));

const CodeBlock = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.default,
  padding: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  fontFamily: 'monospace',
  fontSize: '0.875rem',
  position: 'relative',
  '& pre': {
    margin: 0,
    overflow: 'auto',
    maxHeight: '200px',
  },
}));

const CopyButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  top: theme.spacing(0.5),
  right: theme.spacing(0.5),
  backgroundColor: theme.palette.background.paper,
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

interface AIPairProgrammingProps {
  sessionId: string;
  currentFile: string;
}

export const AIPairProgramming: React.FC<AIPairProgrammingProps> = ({
  sessionId,
  currentFile,
}) => {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const collaborationService = CollaborationService.getInstance();

  useEffect(() => {
    // Subscribe to text changes to generate real-time suggestions
    const subscription = collaborationService.onTextChange().subscribe(
      async (change: TextChange) => {
        await generateSuggestions(change);
      }
    );

    return () => subscription.unsubscribe();
  }, [currentFile]);

  const generateSuggestions = async (change: TextChange) => {
    try {
      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          file: change.file,
          change,
        }),
      });

      const newSuggestions: AISuggestion[] = await response.json();
      setSuggestions(prev => [...newSuggestions, ...prev].slice(0, 10)); // Keep last 10 suggestions
    } catch (error) {
      console.error('Error generating suggestions:', error);
    }
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/ai/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          file: currentFile,
          query,
        }),
      });

      const suggestion: AISuggestion = await response.json();
      setSuggestions(prev => [suggestion, ...prev].slice(0, 10));
      setQuery('');
    } catch (error) {
      console.error('Error submitting query:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
  };

  const handleFeedback = async (suggestionId: string, isHelpful: boolean) => {
    try {
      await fetch('/api/ai/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          suggestionId,
          isHelpful,
          sessionId,
        }),
      });

      // Remove the suggestion after feedback
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  };

  const getSuggestionIcon = (type: AISuggestion['type']) => {
    switch (type) {
      case 'code':
        return <CodeIcon color="primary" />;
      case 'bug':
        return <BugIcon color="error" />;
      case 'improvement':
        return <SuggestionIcon color="success" />;
      default:
        return <AIIcon />;
    }
  };

  return (
    <AIContainer>
      <Box p={2} display="flex" alignItems="center" borderBottom={1} borderColor="divider">
        <AIIcon sx={{ mr: 1 }} />
        <Typography variant="h6">AI Assistant</Typography>
      </Box>

      <SuggestionList>
        {suggestions.map((suggestion) => (
          <ListItem
            key={suggestion.id}
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
                alignItems: 'flex-start',
                cursor: 'pointer',
              }}
              onClick={() => setExpandedId(expandedId === suggestion.id ? null : suggestion.id)}
            >
              <ListItemIcon>{getSuggestionIcon(suggestion.type)}</ListItemIcon>
              <ListItemText
                primary={suggestion.message}
                secondary={new Date(suggestion.timestamp).toLocaleTimeString()}
              />
              <Box>
                <Chip
                  size="small"
                  label={`${Math.round(suggestion.confidence * 100)}%`}
                  color={suggestion.confidence > 0.7 ? 'success' : 'warning'}
                  sx={{ mr: 1 }}
                />
                <IconButton size="small">
                  <ExpandMoreIcon
                    sx={{
                      transform: expandedId === suggestion.id ? 'rotate(180deg)' : 'none',
                      transition: '0.2s',
                    }}
                  />
                </IconButton>
              </Box>
            </Box>

            <Collapse in={expandedId === suggestion.id} sx={{ width: '100%' }}>
              <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1, my: 1 }}>
                {suggestion.explanation && (
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {suggestion.explanation}
                  </Typography>
                )}

                {suggestion.code && (
                  <CodeBlock>
                    <CopyButton
                      size="small"
                      onClick={() => handleCopyCode(suggestion.code!)}
                    >
                      <CopyIcon fontSize="small" />
                    </CopyButton>
                    <pre>{suggestion.code}</pre>
                  </CodeBlock>
                )}

                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <Tooltip title="Helpful">
                    <IconButton
                      size="small"
                      onClick={() => handleFeedback(suggestion.id, true)}
                    >
                      <ThumbUpIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Not Helpful">
                    <IconButton
                      size="small"
                      onClick={() => handleFeedback(suggestion.id, false)}
                    >
                      <ThumbDownIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            </Collapse>
          </ListItem>
        ))}
      </SuggestionList>

      <QueryInput component="form" onSubmit={handleQuerySubmit}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Ask the AI assistant..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isLoading}
          InputProps={{
            endAdornment: isLoading && <CircularProgress size={20} />,
          }}
        />
      </QueryInput>
    </AIContainer>
  );
}; 