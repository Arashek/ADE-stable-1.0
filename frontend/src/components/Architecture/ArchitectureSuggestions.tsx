import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Collapse,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Architecture,
  Lightbulb,
  TrendingUp,
  Security,
  Speed,
  ExpandMore,
  ExpandLess,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { ArchitectureService } from '../../services/architecture/ArchitectureService';

interface Suggestion {
  id: string;
  title: string;
  description: string;
  type: 'performance' | 'security' | 'scalability' | 'maintainability';
  impact: 'high' | 'medium' | 'low';
  details: string;
  recommendations: string[];
  confidence: number;
}

export const ArchitectureSuggestions: React.FC = () => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [detailsDialog, setDetailsDialog] = useState<{
    open: boolean;
    suggestion: Suggestion | null;
  }>({ open: false, suggestion: null });

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const architectureService = ArchitectureService.getInstance();
      const data = await architectureService.analyzeCurrent();
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchSuggestions();
  };

  const handleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleOpenDetails = (suggestion: Suggestion) => {
    setDetailsDialog({ open: true, suggestion });
  };

  const handleCloseDetails = () => {
    setDetailsDialog({ open: false, suggestion: null });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'performance':
        return <Speed color="primary" />;
      case 'security':
        return <Security color="error" />;
      case 'scalability':
        return <TrendingUp color="success" />;
      case 'maintainability':
        return <Architecture color="warning" />;
      default:
        return <Lightbulb />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Architecture Suggestions</Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={handleRefresh} size="small">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <List sx={{ flex: 1, overflow: 'auto' }}>
        {suggestions.map((suggestion) => (
          <React.Fragment key={suggestion.id}>
            <ListItem
              button
              onClick={() => handleExpand(suggestion.id)}
              sx={{
                borderBottom: '1px solid',
                borderColor: 'divider',
              }}
            >
              <ListItemIcon>{getTypeIcon(suggestion.type)}</ListItemIcon>
              <ListItemText
                primary={suggestion.title}
                secondary={
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                    <Chip
                      label={`Impact: ${suggestion.impact}`}
                      size="small"
                      color={getImpactColor(suggestion.impact)}
                    />
                    <Chip
                      label={`Confidence: ${(suggestion.confidence * 100).toFixed(0)}%`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                }
              />
              {expandedId === suggestion.id ? <ExpandLess /> : <ExpandMore />}
            </ListItem>

            <Collapse in={expandedId === suggestion.id}>
              <Box sx={{ p: 2, bgcolor: 'action.hover' }}>
                <Typography variant="body2" paragraph>
                  {suggestion.description}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<InfoIcon />}
                    onClick={() => handleOpenDetails(suggestion)}
                  >
                    View Details
                  </Button>
                </Box>
              </Box>
            </Collapse>
          </React.Fragment>
        ))}
      </List>

      <Dialog
        open={detailsDialog.open}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        {detailsDialog.suggestion && (
          <>
            <DialogTitle>
              {detailsDialog.suggestion.title}
            </DialogTitle>
            <DialogContent>
              <Typography variant="subtitle1" gutterBottom>
                Detailed Analysis
              </Typography>
              <Typography variant="body2" paragraph>
                {detailsDialog.suggestion.details}
              </Typography>

              <Typography variant="subtitle1" gutterBottom>
                Recommendations
              </Typography>
              <List>
                {detailsDialog.suggestion.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Lightbulb color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDetails}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Paper>
  );
}; 