import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  CircularProgress,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Avatar,
  AvatarGroup,
  LinearProgress,
  useTheme,
  alpha
} from '@mui/material';
import {
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  QuestionMark as QuestionMarkIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  ErrorOutline as ErrorOutlineIcon,
  Group as GroupIcon,
  Done as DoneIcon,
  Close as CloseIcon,
  History as HistoryIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import { Agent, AgentStatus } from '../AgentListPanel';

// Decision status enum
export enum DecisionStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  ACHIEVED = 'ACHIEVED',
  DEADLOCKED = 'DEADLOCKED',
  OVERRIDDEN = 'OVERRIDDEN'
}

// Vote type enum
export enum VoteType {
  APPROVE = 'APPROVE',
  REJECT = 'REJECT',
  ABSTAIN = 'ABSTAIN',
  PENDING = 'PENDING'
}

// Agent vote interface
interface AgentVote {
  agentId: string;
  vote: VoteType;
  comment?: string;
  timestamp: Date;
  confidence?: number; // 0-100
}

// Decision interface
export interface Decision {
  id: string;
  title: string;
  description: string;
  status: DecisionStatus;
  createdAt: Date;
  updatedAt: Date;
  resolvedAt?: Date;
  votes: AgentVote[];
  requiredVotes: number;
  requiredApprovalPercentage: number; // 0-100
  category: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  resolution?: string;
  relatedTaskIds?: string[];
}

interface ConsensusBuilderPanelProps {
  agents: Agent[];
  selectedAgentId?: string;
}

/**
 * Helper function to generate mock decisions
 */
const generateMockDecisions = (agents: Agent[], count: number = 10): Decision[] => {
  const decisions: Decision[] = [];
  const statuses = Object.values(DecisionStatus);
  const voteTypes = Object.values(VoteType);
  const priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const;
  
  // Decision titles and categories
  const decisionTitles = [
    'API Authentication Method',
    'Database Schema Design',
    'UI Framework Selection',
    'Error Handling Strategy',
    'Deployment Pipeline Architecture',
    'Testing Framework Selection',
    'Performance Optimization Approach',
    'Caching Strategy',
    'Security Implementation',
    'Documentation Format'
  ];
  
  const categories = [
    'Architecture',
    'Implementation',
    'Design',
    'Security',
    'DevOps',
    'Testing',
    'Performance',
    'Documentation'
  ];
  
  // Generate random decisions
  for (let i = 0; i < count; i++) {
    const createdAt = new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000)); // Within last week
    const updatedAt = new Date(createdAt.getTime() + Math.floor(Math.random() * 24 * 60 * 60 * 1000)); // After created
    
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const titleIndex = Math.floor(Math.random() * decisionTitles.length);
    const category = categories[Math.floor(Math.random() * categories.length)];
    const priority = priorities[Math.floor(Math.random() * priorities.length)];
    
    // Generate votes
    const votes: AgentVote[] = [];
    const requiredVotes = Math.floor(Math.random() * agents.length) + 1; // 1 to agents.length
    
    // Add votes based on status
    if (status !== DecisionStatus.PENDING) {
      // Select random agents to vote
      const votingAgents = [...agents].sort(() => 0.5 - Math.random()).slice(0, Math.min(agents.length, requiredVotes + Math.floor(Math.random() * 3)));
      
      votingAgents.forEach(agent => {
        let vote: VoteType;
        
        if (status === DecisionStatus.ACHIEVED) {
          // Mostly approvals for achieved consensus
          vote = Math.random() > 0.2 ? VoteType.APPROVE : (Math.random() > 0.5 ? VoteType.REJECT : VoteType.ABSTAIN);
        } else if (status === DecisionStatus.DEADLOCKED) {
          // Even split for deadlocked
          vote = Math.random() > 0.5 ? VoteType.APPROVE : VoteType.REJECT;
        } else {
          // Random for others
          vote = voteTypes[Math.floor(Math.random() * (voteTypes.length - 1))]; // Exclude PENDING
        }
        
        const voteTimestamp = new Date(createdAt.getTime() + Math.floor(Math.random() * (updatedAt.getTime() - createdAt.getTime())));
        
        votes.push({
          agentId: agent.id,
          vote,
          comment: `${agent.name} ${vote === VoteType.APPROVE ? 'supports' : vote === VoteType.REJECT ? 'opposes' : 'is neutral on'} this decision.`,
          timestamp: voteTimestamp,
          confidence: Math.floor(Math.random() * 100)
        });
      });
    }
    
    // Set resolvedAt for finished decisions
    let resolvedAt;
    if (status === DecisionStatus.ACHIEVED || status === DecisionStatus.DEADLOCKED || status === DecisionStatus.OVERRIDDEN) {
      resolvedAt = new Date(updatedAt.getTime() + Math.floor(Math.random() * 24 * 60 * 60 * 1000));
    }
    
    // Generate resolution text for resolved decisions
    let resolution;
    if (status === DecisionStatus.ACHIEVED) {
      resolution = `Consensus achieved with ${Math.floor(Math.random() * 30) + 70}% agreement.`;
    } else if (status === DecisionStatus.DEADLOCKED) {
      resolution = 'Deadlocked due to irreconcilable agent perspectives. Manual intervention required.';
    } else if (status === DecisionStatus.OVERRIDDEN) {
      resolution = 'Decision was overridden by administrator due to project requirements.';
    }
    
    decisions.push({
      id: `decision-${i}`,
      title: `${decisionTitles[titleIndex]}`,
      description: `Determine the appropriate ${decisionTitles[titleIndex].toLowerCase()} for the current project component.`,
      status,
      createdAt,
      updatedAt,
      resolvedAt,
      votes,
      requiredVotes,
      requiredApprovalPercentage: Math.floor(Math.random() * 30) + 60, // 60-90%
      category,
      priority,
      resolution,
      relatedTaskIds: Math.random() > 0.5 ? [`task-${Math.floor(Math.random() * 10)}`, `task-${Math.floor(Math.random() * 10)}`] : undefined
    });
  }
  
  return decisions;
};

/**
 * ConsensusBuilderPanel Component - Displays and manages the agent consensus building process
 */
const ConsensusBuilderPanel: React.FC<ConsensusBuilderPanelProps> = ({
  agents,
  selectedAgentId
}) => {
  const theme = useTheme();
  
  // Generate mock decisions
  const [decisions, setDecisions] = useState<Decision[]>(generateMockDecisions(agents));
  
  // Selected decision state
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null);
  
  // Menu state
  const [menuAnchorEl, setMenuAnchorEl] = useState<HTMLElement | null>(null);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState<DecisionStatus | ''>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  
  // Get selected decision
  const selectedDecision = selectedDecisionId ? decisions.find(d => d.id === selectedDecisionId) : null;
  
  // Filter decisions
  const filteredDecisions = decisions.filter(decision => {
    // Filter by selected agent if any
    const agentFilter = selectedAgentId 
      ? decision.votes.some(vote => vote.agentId === selectedAgentId)
      : true;
      
    // Filter by status if selected
    const statusFilterMatch = statusFilter === '' || decision.status === statusFilter;
    
    // Filter by category if selected
    const categoryFilterMatch = categoryFilter === '' || decision.category === categoryFilter;
    
    return agentFilter && statusFilterMatch && categoryFilterMatch;
  });
  
  // Format date
  const formatDate = (date: Date): string => {
    return date.toLocaleString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  // Get agent by ID
  const getAgentById = (id: string) => {
    return agents.find(agent => agent.id === id);
  };
  
  // Calculate consensus stats
  const calculateConsensusStats = (decision: Decision) => {
    const totalVotes = decision.votes.length;
    const approvalVotes = decision.votes.filter(v => v.vote === VoteType.APPROVE).length;
    const rejectionVotes = decision.votes.filter(v => v.vote === VoteType.REJECT).length;
    const abstainVotes = decision.votes.filter(v => v.vote === VoteType.ABSTAIN).length;
    const pendingVotes = decision.votes.filter(v => v.vote === VoteType.PENDING).length;
    
    const approvalPercentage = totalVotes > 0 ? (approvalVotes / totalVotes) * 100 : 0;
    const rejectionPercentage = totalVotes > 0 ? (rejectionVotes / totalVotes) * 100 : 0;
    const abstainPercentage = totalVotes > 0 ? (abstainVotes / totalVotes) * 100 : 0;
    const pendingPercentage = totalVotes > 0 ? (pendingVotes / totalVotes) * 100 : 0;
    
    const consensusAchieved = approvalPercentage >= decision.requiredApprovalPercentage;
    const consensusBlocked = rejectionPercentage > (100 - decision.requiredApprovalPercentage);
    const votingComplete = totalVotes >= decision.requiredVotes;
    
    return {
      totalVotes,
      approvalVotes,
      rejectionVotes,
      abstainVotes,
      pendingVotes,
      approvalPercentage,
      rejectionPercentage,
      abstainPercentage,
      pendingPercentage,
      consensusAchieved,
      consensusBlocked,
      votingComplete
    };
  };
  
  // Get status color
  const getStatusColor = (status: DecisionStatus) => {
    switch (status) {
      case DecisionStatus.PENDING:
        return theme.palette.info.main;
      case DecisionStatus.IN_PROGRESS:
        return theme.palette.primary.main;
      case DecisionStatus.ACHIEVED:
        return theme.palette.success.main;
      case DecisionStatus.DEADLOCKED:
        return theme.palette.warning.main;
      case DecisionStatus.OVERRIDDEN:
        return theme.palette.grey[500];
      default:
        return theme.palette.grey[500];
    }
  };
  
  // Get vote type icon
  const getVoteTypeIcon = (vote: VoteType) => {
    switch (vote) {
      case VoteType.APPROVE:
        return <ThumbUpIcon fontSize="small" color="success" />;
      case VoteType.REJECT:
        return <ThumbDownIcon fontSize="small" color="error" />;
      case VoteType.ABSTAIN:
        return <QuestionMarkIcon fontSize="small" color="disabled" />;
      case VoteType.PENDING:
        return <CircularProgress size={16} />;
      default:
        return <QuestionMarkIcon fontSize="small" />;
    }
  };
  
  // Handle menu open
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };
  
  // Handle menu close
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };
  
  // Reset filters
  const handleResetFilters = () => {
    setStatusFilter('');
    setCategoryFilter('');
  };
  
  // Handle refresh
  const handleRefresh = () => {
    setDecisions(generateMockDecisions(agents));
  };
  
  // Render decision list
  const renderDecisionList = () => {
    return (
      <Paper elevation={0} variant="outlined" sx={{ height: '100%', overflow: 'auto' }}>
        <List sx={{ padding: 0 }}>
          {filteredDecisions.length === 0 ? (
            <ListItem>
              <ListItemText 
                primary="No decisions found" 
                secondary="Try adjusting your filters"
              />
            </ListItem>
          ) : (
            filteredDecisions.map(decision => {
              const stats = calculateConsensusStats(decision);
              
              return (
                <ListItem 
                  key={decision.id}
                  selected={selectedDecisionId === decision.id}
                  button
                  onClick={() => setSelectedDecisionId(decision.id)}
                  sx={{ 
                    borderLeft: `4px solid ${getStatusColor(decision.status)}`,
                    '&.Mui-selected': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    },
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.05),
                    }
                  }}
                >
                  <ListItemIcon>
                    {decision.status === DecisionStatus.ACHIEVED ? (
                      <DoneIcon color="success" />
                    ) : decision.status === DecisionStatus.DEADLOCKED ? (
                      <ErrorOutlineIcon color="warning" />
                    ) : decision.status === DecisionStatus.IN_PROGRESS ? (
                      <GroupIcon color="primary" />
                    ) : decision.status === DecisionStatus.OVERRIDDEN ? (
                      <CloseIcon color="disabled" />
                    ) : (
                      <QuestionMarkIcon color="disabled" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle1">
                          {decision.title}
                        </Typography>
                        <Chip 
                          size="small"
                          label={decision.status.replace('_', ' ')}
                          sx={{
                            color: getStatusColor(decision.status),
                            borderColor: getStatusColor(decision.status),
                            bgcolor: alpha(getStatusColor(decision.status), 0.1)
                          }}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <React.Fragment>
                        <Typography variant="body2" color="textSecondary" component="span">
                          {decision.description}
                        </Typography>
                        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                          <Chip
                            label={`Category: ${decision.category}`}
                            size="small"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                          
                          <Chip
                            label={`Created: ${formatDate(decision.createdAt)}`}
                            size="small"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                          
                          <AvatarGroup max={4} sx={{ '& .MuiAvatar-root': { width: 20, height: 20, fontSize: '0.8rem' } }}>
                            {decision.votes.map(vote => {
                              const agent = getAgentById(vote.agentId);
                              return (
                                <Tooltip key={vote.agentId} title={`${agent?.name || 'Unknown'}: ${vote.vote}`}>
                                  <Avatar 
                                    sx={{ 
                                      bgcolor: agent?.color || theme.palette.grey[500],
                                      border: `2px solid ${
                                        vote.vote === VoteType.APPROVE ? theme.palette.success.main : 
                                        vote.vote === VoteType.REJECT ? theme.palette.error.main :
                                        vote.vote === VoteType.ABSTAIN ? theme.palette.grey[400] :
                                        theme.palette.grey[300]
                                      }`
                                    }}
                                  >
                                    {agent?.name.charAt(0) || '?'}
                                  </Avatar>
                                </Tooltip>
                              );
                            })}
                          </AvatarGroup>
                          
                          {/* Show approval percentage if there are votes */}
                          {stats.totalVotes > 0 && (
                            <Chip
                              label={`Approval: ${Math.round(stats.approvalPercentage)}%`}
                              size="small"
                              variant="outlined"
                              color={stats.consensusAchieved ? 'success' : stats.consensusBlocked ? 'error' : 'default'}
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          )}
                        </Box>
                      </React.Fragment>
                    }
                  />
                </ListItem>
              );
            })
          )}
        </List>
      </Paper>
    );
  };
  
  // Render decision details
  const renderDecisionDetails = () => {
    if (!selectedDecision) {
      return (
        <Paper
          elevation={0}
          variant="outlined"
          sx={{
            height: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            borderStyle: 'dashed'
          }}
        >
          <Box sx={{ textAlign: 'center', p: 3 }}>
            <QuestionMarkIcon color="disabled" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="body1" color="textSecondary">
              Select a decision to view details
            </Typography>
          </Box>
        </Paper>
      );
    }
    
    const stats = calculateConsensusStats(selectedDecision);
    
    return (
      <Paper
        elevation={0}
        variant="outlined"
        sx={{ height: '100%', overflow: 'auto', p: 2 }}
      >
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h6">{selectedDecision.title}</Typography>
            <Typography variant="body2" color="textSecondary">
              {selectedDecision.description}
            </Typography>
            <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip 
                size="small" 
                label={selectedDecision.category} 
                variant="outlined" 
              />
              <Chip 
                size="small" 
                label={`Priority: ${selectedDecision.priority}`}
                color={
                  selectedDecision.priority === 'CRITICAL' ? 'error' :
                  selectedDecision.priority === 'HIGH' ? 'warning' :
                  selectedDecision.priority === 'MEDIUM' ? 'info' : 'success'
                }
                variant="outlined"
              />
              <Chip 
                size="small" 
                label={`Required votes: ${selectedDecision.requiredVotes}`}
                variant="outlined"
              />
              <Chip 
                size="small" 
                label={`Required approval: ${selectedDecision.requiredApprovalPercentage}%`}
                variant="outlined"
              />
            </Box>
          </Box>
          <Chip 
            label={selectedDecision.status.replace('_', ' ')}
            sx={{
              color: getStatusColor(selectedDecision.status),
              borderColor: getStatusColor(selectedDecision.status),
              bgcolor: alpha(getStatusColor(selectedDecision.status), 0.1)
            }}
            variant="outlined"
          />
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        {/* Consensus progress */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Consensus Progress
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper elevation={0} variant="outlined" sx={{ p: 2 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Approval Rate
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress 
                      variant="determinate"
                      value={stats.approvalPercentage}
                      color={stats.consensusAchieved ? 'success' : 'primary'}
                      sx={{ height: 8, borderRadius: 1 }}
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      {`${Math.round(stats.approvalPercentage)}%`}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="textSecondary">
                    0%
                  </Typography>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: theme.palette.warning.main,
                      position: 'absolute',
                      left: `${selectedDecision.requiredApprovalPercentage}%`,
                      transform: 'translateX(-50%)'
                    }}
                  >
                    Required: {selectedDecision.requiredApprovalPercentage}%
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    100%
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper elevation={0} variant="outlined" sx={{ p: 2 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Voting Status
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip 
                    icon={<ThumbUpIcon fontSize="small" />}
                    label={`${stats.approvalVotes} Approve`}
                    size="small"
                    variant="outlined"
                    color="success"
                  />
                  <Chip 
                    icon={<ThumbDownIcon fontSize="small" />}
                    label={`${stats.rejectionVotes} Reject`}
                    size="small"
                    variant="outlined"
                    color="error"
                  />
                  <Chip 
                    icon={<QuestionMarkIcon fontSize="small" />}
                    label={`${stats.abstainVotes} Abstain`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>
        
        {/* Vote list */}
        <Typography variant="subtitle1" gutterBottom>
          Agent Votes
        </Typography>
        
        <List>
          {selectedDecision.votes.length === 0 ? (
            <ListItem>
              <ListItemText 
                primary="No votes yet" 
                secondary="Waiting for agents to cast their votes"
              />
            </ListItem>
          ) : (
            selectedDecision.votes.map(vote => {
              const agent = getAgentById(vote.agentId);
              
              return (
                <ListItem key={vote.agentId}>
                  <ListItemIcon>
                    {getVoteTypeIcon(vote.vote)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body1">
                          {agent?.name || 'Unknown Agent'}
                        </Typography>
                        {vote.confidence !== undefined && (
                          <Chip
                            size="small"
                            label={`${vote.confidence}% confidence`}
                            sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                            variant="outlined"
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <React.Fragment>
                        <Typography variant="body2" color="textSecondary">
                          {vote.comment || `Vote: ${vote.vote}`}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {formatDate(vote.timestamp)}
                        </Typography>
                      </React.Fragment>
                    }
                  />
                </ListItem>
              );
            })
          )}
        </List>
        
        {/* Resolution for resolved decisions */}
        {selectedDecision.resolution && (
          <React.Fragment>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Resolution
              </Typography>
              <Paper elevation={0} sx={{ p: 2, bgcolor: alpha(theme.palette.background.default, 0.5) }}>
                <Typography variant="body2">
                  {selectedDecision.resolution}
                </Typography>
                {selectedDecision.resolvedAt && (
                  <Typography variant="caption" color="textSecondary" display="block" sx={{ mt: 1 }}>
                    Resolved on {formatDate(selectedDecision.resolvedAt)}
                  </Typography>
                )}
              </Paper>
            </Box>
          </React.Fragment>
        )}
      </Paper>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Consensus Builder
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<FilterListIcon />}
            onClick={handleResetFilters}
          >
            {statusFilter || categoryFilter ? 'Clear Filters' : 'Filter'}
          </Button>
          
          <IconButton size="small" onClick={handleRefresh}>
            <RefreshIcon />
          </IconButton>
          
          <IconButton size="small" onClick={handleMenuOpen}>
            <MoreVertIcon />
          </IconButton>
        </Box>
      </Box>
      
      {/* Status filters */}
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {Object.values(DecisionStatus).map(status => (
          <Chip
            key={status}
            label={status.replace('_', ' ')}
            size="small"
            variant={statusFilter === status ? 'filled' : 'outlined'}
            onClick={() => setStatusFilter(prev => prev === status ? '' : status)}
            sx={{ 
              color: statusFilter === status ? theme.palette.getContrastText(getStatusColor(status)) : getStatusColor(status),
              bgcolor: statusFilter === status ? getStatusColor(status) : 'transparent',
              borderColor: getStatusColor(status)
            }}
          />
        ))}
      </Box>
      
      {/* Main content */}
      <Box sx={{ flexGrow: 1, display: 'flex', gap: 2, overflow: 'hidden' }}>
        {/* Decision list */}
        <Box sx={{ width: '40%', height: '100%' }}>
          {renderDecisionList()}
        </Box>
        
        {/* Decision details */}
        <Box sx={{ width: '60%', height: '100%' }}>
          {renderDecisionDetails()}
        </Box>
      </Box>
      
      {/* Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRefresh}>
          <RefreshIcon fontSize="small" sx={{ mr: 1 }} />
          Refresh Data
        </MenuItem>
        <MenuItem onClick={handleResetFilters}>
          <FilterListIcon fontSize="small" sx={{ mr: 1 }} />
          Clear Filters
        </MenuItem>
        <MenuItem 
          onClick={() => {
            handleMenuClose();
            setSelectedDecisionId(null);
          }}
        >
          <HistoryIcon fontSize="small" sx={{ mr: 1 }} />
          Clear Selection
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ConsensusBuilderPanel;
