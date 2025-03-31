import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Grid,
  Divider,
  IconButton,
  Tooltip,
  Collapse,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CodeReviewResponse } from '../../types/agent.types';

interface ReviewResultsProps {
  result: CodeReviewResponse;
}

export const ReviewResults: React.FC<ReviewResultsProps> = ({ result }) => {
  const [expandedComments, setExpandedComments] = React.useState<Set<number>>(new Set());

  const toggleComment = (lineNumber: number) => {
    const newExpanded = new Set(expandedComments);
    if (newExpanded.has(lineNumber)) {
      newExpanded.delete(lineNumber);
    } else {
      newExpanded.add(lineNumber);
    }
    setExpandedComments(newExpanded);
  };

  const getCommentIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getCommentColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Code Review Results</Typography>
        <Box>
          {result.review_types.map((type) => (
            <Chip
              key={type}
              label={type}
              color="primary"
              size="small"
              sx={{ mr: 1 }}
            />
          ))}
        </Box>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Summary
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography>{result.summary}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Comments
          </Typography>
          <List>
            {result.comments.map((comment, index) => (
              <React.Fragment key={index}>
                <ListItem
                  button
                  onClick={() => toggleComment(comment.line_number)}
                  sx={{
                    bgcolor: 'background.default',
                    mb: 1,
                    borderRadius: 1,
                  }}
                >
                  <ListItemIcon>
                    {getCommentIcon(comment.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center">
                        <Typography variant="subtitle2" sx={{ mr: 1 }}>
                          Line {comment.line_number}
                        </Typography>
                        <Chip
                          label={comment.type}
                          color={getCommentColor(comment.type)}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={comment.message}
                  />
                  {comment.suggestion && (
                    <IconButton size="small">
                      {expandedComments.has(comment.line_number) ? (
                        <ExpandLessIcon />
                      ) : (
                        <ExpandMoreIcon />
                      )}
                    </IconButton>
                  )}
                </ListItem>
                {comment.suggestion && (
                  <Collapse
                    in={expandedComments.has(comment.line_number)}
                    timeout="auto"
                    unmountOnExit
                  >
                    <Box sx={{ ml: 4, mb: 2 }}>
                      <Typography variant="subtitle2" color="primary" gutterBottom>
                        Suggestion
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography>{comment.suggestion}</Typography>
                      </Paper>
                    </Box>
                  </Collapse>
                )}
              </React.Fragment>
            ))}
          </List>
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom>
            Review Details
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            <Chip
              label={`File: ${result.file_path}`}
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