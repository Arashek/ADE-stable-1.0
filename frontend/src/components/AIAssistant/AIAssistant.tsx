import React, { useState, useEffect, useCallback } from 'react';
import { Box, Paper, IconButton, TextField, Typography, List, ListItem, ListItemText, ListItemIcon, Collapse, Tooltip, CircularProgress, Menu, MenuItem, Badge, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CodeIcon from '@mui/icons-material/Code';
import TerminalIcon from '@mui/icons-material/Terminal';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import SettingsIcon from '@mui/icons-material/Settings';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import HistoryIcon from '@mui/icons-material/History';
import SaveIcon from '@mui/icons-material/Save';
import { AIAssistantState, AIAssistantHistory, AIAssistantSuggestion, AIAssistantSettings, AIAssistantAnalytics } from '../../interfaces/ai-assistant';
import { AIAssistantSettingsPanel } from './AIAssistantSettings';
import { AIAssistantAnalyticsPanel } from './AIAssistantAnalytics';

const AssistantContainer = styled(Paper)(({ theme }) => ({
    position: 'fixed',
    right: theme.spacing(2),
    bottom: theme.spacing(2),
    width: 400,
    maxHeight: 600,
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1000,
    boxShadow: theme.shadows[4],
}));

const AssistantHeader = styled(Box)(({ theme }) => ({
    padding: theme.spacing(1),
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
}));

const AssistantContent = styled(Box)(({ theme }) => ({
    flex: 1,
    overflow: 'auto',
    padding: theme.spacing(2),
}));

const MessageList = styled(List)(({ theme }) => ({
    padding: theme.spacing(1),
}));

const MessageItem = styled(ListItem)(({ theme }) => ({
    marginBottom: theme.spacing(1),
    borderRadius: theme.shape.borderRadius,
    '&.user': {
        backgroundColor: theme.palette.primary.light,
        marginLeft: theme.spacing(4),
    },
    '&.assistant': {
        backgroundColor: theme.palette.background.paper,
        marginRight: theme.spacing(4),
    },
}));

const SuggestionList = styled(List)(({ theme }) => ({
    marginTop: theme.spacing(2),
}));

const SuggestionItem = styled(ListItem)(({ theme }) => ({
    backgroundColor: theme.palette.background.default,
    borderRadius: theme.spacing(1),
    marginBottom: theme.spacing(1),
    '&:hover': {
        backgroundColor: theme.palette.action.hover,
    },
}));

const SolutionList = styled(List)(({ theme }) => ({
    marginTop: theme.spacing(1),
    marginLeft: theme.spacing(2),
}));

const SolutionItem = styled(ListItem)(({ theme }) => ({
    backgroundColor: theme.palette.background.paper,
    borderRadius: theme.spacing(1),
    marginBottom: theme.spacing(1),
    '&:hover': {
        backgroundColor: theme.palette.action.hover,
    },
}));

const SolutionMetrics = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: theme.spacing(1),
    marginTop: theme.spacing(1),
}));

const MetricChip = styled(Chip)(({ theme }) => ({
    marginRight: theme.spacing(0.5),
}));

interface AIAssistantProps {
    state: AIAssistantState;
    analytics: AIAssistantAnalytics;
    onSendMessage: (message: string) => void;
    onApplySuggestion: (suggestion: AIAssistantSuggestion, solutionIndex?: number) => void;
    onRejectSuggestion: (suggestion: AIAssistantSuggestion) => void;
    onToggleExpand: () => void;
    onFeedback: (suggestionId: string, rating: 'helpful' | 'not_helpful') => void;
    onSettingsChange: (settings: AIAssistantSettings) => void;
    onSaveHistory: () => void;
}

export const AIAssistant: React.FC<AIAssistantProps> = ({
    state,
    analytics,
    onSendMessage,
    onApplySuggestion,
    onRejectSuggestion,
    onToggleExpand,
    onFeedback,
    onSettingsChange,
    onSaveHistory,
}) => {
    const [message, setMessage] = useState('');
    const [expanded, setExpanded] = useState(true);
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [analyticsOpen, setAnalyticsOpen] = useState(false);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedSuggestion, setSelectedSuggestion] = useState<AIAssistantSuggestion | null>(null);
    const [selectedSolution, setSelectedSolution] = useState<number | null>(null);
    const [solutionDialogOpen, setSolutionDialogOpen] = useState(false);

    const handleSendMessage = useCallback(() => {
        if (message.trim()) {
            onSendMessage(message.trim());
            setMessage('');
        }
    }, [message, onSendMessage]);

    const handleKeyPress = useCallback((event: React.KeyboardEvent) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    }, [handleSendMessage]);

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const handleSuggestionClick = (suggestion: AIAssistantSuggestion) => {
        setSelectedSuggestion(suggestion);
        handleMenuOpen(new Event('click') as any);
    };

    const handleApplySuggestion = () => {
        if (selectedSuggestion) {
            onApplySuggestion(selectedSuggestion);
            handleMenuClose();
        }
    };

    const handleRejectSuggestion = () => {
        if (selectedSuggestion) {
            onRejectSuggestion(selectedSuggestion);
            handleMenuClose();
        }
    };

    const handleFeedback = (rating: 'helpful' | 'not_helpful') => {
        if (selectedSuggestion) {
            onFeedback(selectedSuggestion.id, rating);
            handleMenuClose();
        }
    };

    const handleSolutionSelect = (suggestion: AIAssistantSuggestion, solutionIndex: number) => {
        setSelectedSuggestion(suggestion);
        setSelectedSolution(solutionIndex);
        setSolutionDialogOpen(true);
    };

    const handleApplySolution = () => {
        if (selectedSuggestion && selectedSolution !== null) {
            onApplySuggestion(selectedSuggestion, selectedSolution);
            setSolutionDialogOpen(false);
        }
    };

    const renderSolutionMetrics = (solution: any) => {
        if (!solution.metrics) return null;

        return (
            <SolutionMetrics>
                <MetricChip
                    size="small"
                    label={`Effectiveness: ${(solution.metrics.effectiveness * 100).toFixed(1)}%`}
                    color={solution.metrics.effectiveness >= 0.8 ? 'success' : 'default'}
                />
                <MetricChip
                    size="small"
                    label={`Impact: ${(solution.metrics.impact * 100).toFixed(1)}%`}
                    color={solution.metrics.impact >= 0.8 ? 'success' : 'default'}
                />
                <MetricChip
                    size="small"
                    label={`Complexity: ${(solution.metrics.complexity * 100).toFixed(1)}%`}
                    color={solution.metrics.complexity <= 0.3 ? 'success' : 'default'}
                />
                <MetricChip
                    size="small"
                    label={`Maintainability: ${(solution.metrics.maintainability * 100).toFixed(1)}%`}
                    color={solution.metrics.maintainability >= 0.8 ? 'success' : 'default'}
                />
            </SolutionMetrics>
        );
    };

    const renderSolutions = (suggestion: AIAssistantSuggestion) => {
        if (!suggestion.solutions || suggestion.solutions.length === 0) return null;

        return (
            <SolutionList>
                <Typography variant="subtitle2" gutterBottom>
                    Available Solutions
                </Typography>
                {suggestion.solutions.map((solution, index) => (
                    <SolutionItem
                        key={index}
                        onClick={() => handleSolutionSelect(suggestion, index)}
                        sx={{ cursor: 'pointer' }}
                    >
                        <ListItemText
                            primary={`Solution ${index + 1}`}
                            secondary={
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        {solution.description}
                                    </Typography>
                                    {renderSolutionMetrics(solution)}
                                </Box>
                            }
                        />
                        <IconButton
                            size="small"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleSolutionSelect(suggestion, index);
                            }}
                        >
                            <CodeIcon />
                        </IconButton>
                    </SolutionItem>
                ))}
            </SolutionList>
        );
    };

    return (
        <>
            <AssistantContainer>
                <AssistantHeader>
                    <Box display="flex" alignItems="center">
                        <SmartToyIcon sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">AI Assistant</Typography>
                    </Box>
                    <Box>
                        <Tooltip title="Save History">
                            <IconButton size="small" onClick={onSaveHistory}>
                                <SaveIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Analytics">
                            <IconButton size="small" onClick={() => setAnalyticsOpen(true)}>
                                <Badge badgeContent={analytics.totalInteractions} color="primary">
                                    <AnalyticsIcon />
                                </Badge>
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Settings">
                            <IconButton size="small" onClick={() => setSettingsOpen(true)}>
                                <SettingsIcon />
                            </IconButton>
                        </Tooltip>
                        <IconButton size="small" onClick={onToggleExpand}>
                            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                    </Box>
                </AssistantHeader>
                <Collapse in={expanded}>
                    <AssistantContent>
                        <MessageList>
                            {state.history.map((item: AIAssistantHistory) => (
                                <MessageItem
                                    key={item.id}
                                    className={item.type}
                                    alignItems="flex-start"
                                >
                                    <ListItemIcon>
                                        {item.type === 'user' ? <SmartToyIcon /> : <CodeIcon />}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.content}
                                        secondary={item.metadata?.command && (
                                            <Typography variant="caption" color="textSecondary">
                                                Command: {item.metadata.command}
                                            </Typography>
                                        )}
                                    />
                                </MessageItem>
                            ))}
                        </MessageList>

                        {state.suggestions.length > 0 && (
                            <SuggestionList>
                                <Typography variant="subtitle2" gutterBottom>
                                    Suggestions
                                </Typography>
                                {state.suggestions.map((suggestion: AIAssistantSuggestion) => (
                                    <SuggestionItem
                                        key={suggestion.id}
                                        onClick={() => handleSuggestionClick(suggestion)}
                                        sx={{ cursor: 'pointer' }}
                                    >
                                        <ListItemText
                                            primary={suggestion.content}
                                            secondary={`Confidence: ${(suggestion.confidence * 100).toFixed(1)}%`}
                                        />
                                        <Box>
                                            <Tooltip title="Apply">
                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleSuggestionClick(suggestion);
                                                    }}
                                                >
                                                    <CodeIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Reject">
                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onRejectSuggestion(suggestion);
                                                    }}
                                                >
                                                    <ThumbDownIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Helpful">
                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onFeedback(suggestion.id, 'helpful');
                                                    }}
                                                >
                                                    <ThumbUpIcon />
                                                </IconButton>
                                            </Tooltip>
                                        </Box>
                                    </SuggestionItem>
                                ))}
                                {renderSolutions(selectedSuggestion)}
                            </SuggestionList>
                        )}

                        {state.isProcessing && (
                            <Box display="flex" justifyContent="center" mt={2}>
                                <CircularProgress size={24} />
                            </Box>
                        )}
                    </AssistantContent>
                    <Box p={2} borderTop={1} borderColor="divider">
                        <TextField
                            fullWidth
                            multiline
                            rows={2}
                            variant="outlined"
                            placeholder="Ask for help or type a command..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            disabled={state.isProcessing}
                            InputProps={{
                                endAdornment: (
                                    <IconButton
                                        color="primary"
                                        onClick={handleSendMessage}
                                        disabled={state.isProcessing}
                                    >
                                        <SendIcon />
                                    </IconButton>
                                ),
                            }}
                        />
                    </Box>
                </Collapse>
            </AssistantContainer>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                <MenuItem onClick={handleApplySuggestion}>
                    <CodeIcon sx={{ mr: 1 }} /> Apply Suggestion
                </MenuItem>
                <MenuItem onClick={handleRejectSuggestion}>
                    <ThumbDownIcon sx={{ mr: 1 }} /> Reject Suggestion
                </MenuItem>
                <MenuItem onClick={() => handleFeedback('helpful')}>
                    <ThumbUpIcon sx={{ mr: 1 }} /> Mark as Helpful
                </MenuItem>
                <MenuItem onClick={() => handleFeedback('not_helpful')}>
                    <ThumbDownIcon sx={{ mr: 1 }} /> Mark as Not Helpful
                </MenuItem>
            </Menu>

            <AIAssistantSettingsPanel
                open={settingsOpen}
                settings={state.settings}
                onClose={() => setSettingsOpen(false)}
                onSave={(settings) => {
                    onSettingsChange(settings);
                    setSettingsOpen(false);
                }}
            />

            <AIAssistantAnalyticsPanel
                open={analyticsOpen}
                analytics={analytics}
                onClose={() => setAnalyticsOpen(false)}
            />

            <Dialog
                open={solutionDialogOpen}
                onClose={() => setSolutionDialogOpen(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>Select Solution</DialogTitle>
                <DialogContent>
                    {selectedSuggestion && selectedSolution !== null && (
                        <Box>
                            <Typography variant="subtitle1" gutterBottom>
                                {selectedSuggestion.content}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                Solution {selectedSolution + 1}
                            </Typography>
                            <Paper
                                variant="outlined"
                                sx={{
                                    p: 2,
                                    my: 2,
                                    fontFamily: 'monospace',
                                    whiteSpace: 'pre-wrap',
                                }}
                            >
                                {selectedSuggestion.solutions[selectedSolution].code}
                            </Paper>
                            {renderSolutionMetrics(selectedSuggestion.solutions[selectedSolution])}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setSolutionDialogOpen(false)}>Cancel</Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleApplySolution}
                    >
                        Apply Solution
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}; 