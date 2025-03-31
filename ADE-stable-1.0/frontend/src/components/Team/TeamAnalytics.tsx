import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  Chip,
} from '@mui/material';
import {
  Person as PersonIcon,
  Group as GroupIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Chat as ChatIcon,
  Code as CodeIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

interface TeamMemberStats {
  id: string;
  name: string;
  avatar?: string;
  tasksCompleted: number;
  tasksInProgress: number;
  tasksOverdue: number;
  commits: number;
  pullRequests: number;
  comments: number;
  responseTime: string;
}

interface TeamMetrics {
  totalTasks: number;
  completedTasks: number;
  inProgressTasks: number;
  overdueTasks: number;
  totalCommits: number;
  totalPullRequests: number;
  totalComments: number;
  averageResponseTime: string;
  teamVelocity: number;
  codeReviewTime: string;
}

const mockTeamStats: TeamMemberStats[] = [
  {
    id: '1',
    name: 'John Doe',
    avatar: 'https://via.placeholder.com/40',
    tasksCompleted: 12,
    tasksInProgress: 3,
    tasksOverdue: 1,
    commits: 45,
    pullRequests: 8,
    comments: 32,
    responseTime: '2.5h',
  },
  {
    id: '2',
    name: 'Jane Smith',
    avatar: 'https://via.placeholder.com/40',
    tasksCompleted: 8,
    tasksInProgress: 2,
    tasksOverdue: 0,
    commits: 38,
    pullRequests: 6,
    comments: 28,
    responseTime: '1.8h',
  },
];

const mockTeamMetrics: TeamMetrics = {
  totalTasks: 25,
  completedTasks: 20,
  inProgressTasks: 5,
  overdueTasks: 1,
  totalCommits: 83,
  totalPullRequests: 14,
  totalComments: 60,
  averageResponseTime: '2.1h',
  teamVelocity: 85,
  codeReviewTime: '4.2h',
};

const TeamAnalytics: React.FC = () => {
  const calculateProgress = (completed: number, total: number) => {
    return (completed / total) * 100;
  };

  const getVelocityColor = (velocity: number) => {
    if (velocity >= 80) return 'success';
    if (velocity >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Team Overview Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <GroupIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Team Size</Typography>
              </Box>
              <Typography variant="h4">{mockTeamStats.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Active Members
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Team Velocity</Typography>
              </Box>
              <Typography variant="h4">{mockTeamMetrics.teamVelocity}%</Typography>
              <Typography variant="body2" color="text.secondary">
                Last Sprint
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Tasks Completed</Typography>
              </Box>
              <Typography variant="h4">{mockTeamMetrics.completedTasks}</Typography>
              <Typography variant="body2" color="text.secondary">
                Out of {mockTeamMetrics.totalTasks}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ScheduleIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Avg Response Time</Typography>
              </Box>
              <Typography variant="h4">{mockTeamMetrics.averageResponseTime}</Typography>
              <Typography variant="body2" color="text.secondary">
                To Comments & Reviews
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Task Progress */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Task Progress
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Overall Progress</Typography>
                <Typography variant="body2">
                  {calculateProgress(mockTeamMetrics.completedTasks, mockTeamMetrics.totalTasks).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={calculateProgress(mockTeamMetrics.completedTasks, mockTeamMetrics.totalTasks)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">In Progress</Typography>
                <Typography variant="body2">
                  {calculateProgress(mockTeamMetrics.inProgressTasks, mockTeamMetrics.totalTasks).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={calculateProgress(mockTeamMetrics.inProgressTasks, mockTeamMetrics.totalTasks)}
                color="warning"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Overdue</Typography>
                <Typography variant="body2">
                  {calculateProgress(mockTeamMetrics.overdueTasks, mockTeamMetrics.totalTasks).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={calculateProgress(mockTeamMetrics.overdueTasks, mockTeamMetrics.totalTasks)}
                color="error"
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Team Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Team Activity
            </Typography>
            <List>
              <ListItem>
                <ListItemAvatar>
                  <Avatar>
                    <CodeIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary="Total Commits"
                  secondary={`${mockTeamMetrics.totalCommits} commits in the last sprint`}
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemAvatar>
                  <Avatar>
                    <AssignmentIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary="Pull Requests"
                  secondary={`${mockTeamMetrics.totalPullRequests} PRs created and reviewed`}
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemAvatar>
                  <Avatar>
                    <ChatIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary="Comments"
                  secondary={`${mockTeamMetrics.totalComments} comments on code and tasks`}
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemAvatar>
                  <Avatar>
                    <ScheduleIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary="Code Review Time"
                  secondary={`Average time to review: ${mockTeamMetrics.codeReviewTime}`}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* Individual Performance */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Individual Performance
            </Typography>
            <List>
              {mockTeamStats.map((member) => (
                <React.Fragment key={member.id}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar src={member.avatar}>
                        <PersonIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={member.name}
                      secondary={
                        <Box>
                          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                            <Chip
                              size="small"
                              label={`${member.tasksCompleted} completed`}
                              color="success"
                            />
                            <Chip
                              size="small"
                              label={`${member.tasksInProgress} in progress`}
                              color="warning"
                            />
                            <Chip
                              size="small"
                              label={`${member.tasksOverdue} overdue`}
                              color="error"
                            />
                          </Box>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip
                              size="small"
                              label={`${member.commits} commits`}
                              icon={<CodeIcon />}
                            />
                            <Chip
                              size="small"
                              label={`${member.pullRequests} PRs`}
                              icon={<AssignmentIcon />}
                            />
                            <Chip
                              size="small"
                              label={`${member.comments} comments`}
                              icon={<ChatIcon />}
                            />
                            <Chip
                              size="small"
                              label={`${member.responseTime} avg response`}
                              icon={<ScheduleIcon />}
                            />
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TeamAnalytics; 