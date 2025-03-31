import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    Box,
    Typography,
    Grid,
    Paper,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Divider,
} from '@mui/material';
import {
    Timeline as TimelineIcon,
    Speed as SpeedIcon,
    CheckCircle as CheckCircleIcon,
    Cancel as CancelIcon,
    TrendingUp as TrendingUpIcon,
    Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { AIAssistantAnalytics } from '../../interfaces/ai-assistant';

interface AIAssistantAnalyticsProps {
    open: boolean;
    analytics: AIAssistantAnalytics;
    onClose: () => void;
}

export const AIAssistantAnalyticsPanel: React.FC<AIAssistantAnalyticsProps> = ({
    open,
    analytics,
    onClose,
}) => {
    const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;
    const formatTime = (ms: number) => `${(ms / 1000).toFixed(2)}s`;

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>AI Assistant Analytics</DialogTitle>
            <DialogContent>
                <Box sx={{ mt: 2 }}>
                    <Grid container spacing={3}>
                        {/* Overview Stats */}
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Overview
                                </Typography>
                                <List>
                                    <ListItem>
                                        <ListItemText
                                            primary="Total Interactions"
                                            secondary={analytics.totalInteractions}
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemText
                                            primary="Average Confidence"
                                            secondary={formatPercentage(analytics.averageConfidence)}
                                        />
                                    </ListItem>
                                </List>
                            </Paper>
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Suggestion Stats
                                </Typography>
                                <List>
                                    <ListItem>
                                        <ListItemIcon>
                                            <CheckCircleIcon color="success" />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary="Successful Suggestions"
                                            secondary={analytics.successfulSuggestions}
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemIcon>
                                            <CancelIcon color="error" />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary="Rejected Suggestions"
                                            secondary={analytics.rejectedSuggestions}
                                        />
                                    </ListItem>
                                </List>
                            </Paper>
                        </Grid>

                        {/* Performance Metrics */}
                        <Grid item xs={12}>
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    Performance
                                </Typography>
                                <List>
                                    <ListItem>
                                        <ListItemText
                                            primary="Average Response Time"
                                            secondary={formatTime(analytics.performance.averageResponseTime)}
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemText
                                            primary="Error Rate"
                                            secondary={formatPercentage(analytics.performance.errorRate)}
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemText
                                            primary="Suggestion Accuracy"
                                            secondary={formatPercentage(analytics.performance.suggestionAccuracy)}
                                        />
                                    </ListItem>
                                </List>
                            </Paper>
                        </Grid>

                        {/* User Feedback */}
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                                    User Feedback
                                </Typography>
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" color="textSecondary" gutterBottom>
                                        Helpful
                                    </Typography>
                                    <LinearProgress
                                        variant="determinate"
                                        value={(analytics.userFeedback.helpful / (analytics.userFeedback.helpful + analytics.userFeedback.notHelpful)) * 100}
                                        color="success"
                                    />
                                </Box>
                                <Box>
                                    <Typography variant="body2" color="textSecondary" gutterBottom>
                                        Not Helpful
                                    </Typography>
                                    <LinearProgress
                                        variant="determinate"
                                        value={(analytics.userFeedback.notHelpful / (analytics.userFeedback.helpful + analytics.userFeedback.notHelpful)) * 100}
                                        color="error"
                                    />
                                </Box>
                            </Paper>
                        </Grid>

                        {/* Popular Commands */}
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    Popular Commands
                                </Typography>
                                <List>
                                    {analytics.popularCommands.map((command, index) => (
                                        <React.Fragment key={command.name}>
                                            <ListItem>
                                                <ListItemText
                                                    primary={command.name}
                                                    secondary={`Used ${command.count} times`}
                                                />
                                            </ListItem>
                                            {index < analytics.popularCommands.length - 1 && <Divider />}
                                        </React.Fragment>
                                    ))}
                                </List>
                            </Paper>
                        </Grid>
                    </Grid>
                </Box>
            </DialogContent>
        </Dialog>
    );
}; 