import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  TextField,
  Button,
  Chip,
  Avatar,
  Tabs,
  Tab,
  IconButton,
  Divider,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  Merge as MergeIcon,
  Close as CloseIcon,
  Comment as CommentIcon,
  Check as CheckIcon,
  Warning as WarningIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import UnifiedChat from '../components/shared/UnifiedChat';

interface PullRequest {
  id: string;
  title: string;
  description: string;
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  status: 'open' | 'merged' | 'closed';
  createdAt: string;
  updatedAt: string;
  sourceBranch: string;
  targetBranch: string;
  repository: string;
  commits: number;
  comments: number;
  reviewers: Array<{
    id: string;
    name: string;
    avatar: string;
    status?: 'approved' | 'requested_changes' | 'commented';
  }>;
  checks: Array<{
    name: string;
    status: 'success' | 'failure' | 'pending';
    description: string;
  }>;
  files: Array<{
    path: string;
    status: 'added' | 'modified' | 'deleted';
    additions: number;
    deletions: number;
    diff: string;
  }>;
}

const PullRequests: React.FC = () => {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [selectedPR, setSelectedPR] = useState<PullRequest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchPullRequests();
  }, []);

  const fetchPullRequests = async () => {
    try {
      // TODO: Fetch pull requests from API
      const mockData: PullRequest[] = [
        {
          id: '1',
          title: 'Add authentication feature',
          description: 'Implement user authentication using JWT',
          author: {
            id: '1',
            name: 'John Doe',
            avatar: 'https://mui.com/static/images/avatar/1.jpg',
          },
          status: 'open',
          createdAt: '2024-03-24T10:00:00Z',
          updatedAt: '2024-03-24T15:30:00Z',
          sourceBranch: 'feature/auth',
          targetBranch: 'main',
          repository: 'org/repo',
          commits: 5,
          comments: 3,
          reviewers: [
            {
              id: '2',
              name: 'Jane Smith',
              avatar: 'https://mui.com/static/images/avatar/2.jpg',
              status: 'approved',
            },
          ],
          checks: [
            {
              name: 'CI/CD Pipeline',
              status: 'success',
              description: 'All tests passed',
            },
          ],
          files: [
            {
              path: 'src/auth/auth.service.ts',
              status: 'added',
              additions: 50,
              deletions: 0,
              diff: `@@ -0,0 +1,50 @@
+ import { Injectable } from '@nestjs/common';
+ import { JwtService } from '@nestjs/jwt';
+ 
+ @Injectable()
+ export class AuthService {
+   constructor(private jwtService: JwtService) {}
+ 
+   async validateUser(username: string, password: string): Promise<any> {
+     // Implementation
+   }
+ }`,
            },
          ],
        },
        // Add more mock data...
      ];
      setPullRequests(mockData);
    } catch (err) {
      setError('Failed to fetch pull requests');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const toggleStatusFilter = (status: string) => {
    setStatusFilter((prev) =>
      prev.includes(status)
        ? prev.filter((s) => s !== status)
        : [...prev, status]
    );
  };

  const handleSendMessage = (message: string, threadId?: string) => {
    // TODO: Implement message sending to backend
    console.log('Sending message:', message, 'to thread:', threadId);
  };

  const filteredPRs = pullRequests.filter((pr) => {
    const matchesSearch =
      pr.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pr.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter.length === 0 || statusFilter.includes(pr.status);
    return matchesSearch && matchesStatus;
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {/* Pull Request List */}
        <Grid item xs={12} md={selectedPR ? 4 : 12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 2 }}>
              <TextField
                fullWidth
                placeholder="Search pull requests..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                size="small"
              />
              <IconButton onClick={handleFilterClick}>
                <FilterIcon />
              </IconButton>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                size="small"
              >
                New PR
              </Button>
            </Box>

            <List>
              {filteredPRs.map((pr) => (
                <ListItem
                  key={pr.id}
                  button
                  selected={selectedPR?.id === pr.id}
                  onClick={() => setSelectedPR(pr)}
                >
                  <ListItemIcon>
                    {pr.status === 'merged' ? (
                      <MergeIcon color="success" />
                    ) : pr.status === 'closed' ? (
                      <CloseIcon color="error" />
                    ) : (
                      <GitHubIcon color="primary" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={pr.title}
                    secondary={`#${pr.id} opened by ${pr.author.name}`}
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label={pr.status}
                      color={
                        pr.status === 'merged'
                          ? 'success'
                          : pr.status === 'closed'
                          ? 'error'
                          : 'primary'
                      }
                      size="small"
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Pull Request Details */}
        {selectedPR && (
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Box>
                  <Typography variant="h5" gutterBottom>
                    {selectedPR.title}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={selectedPR.status}
                      color={
                        selectedPR.status === 'merged'
                          ? 'success'
                          : selectedPR.status === 'closed'
                          ? 'error'
                          : 'primary'
                      }
                    />
                    <Typography variant="body2" color="text.secondary">
                      {selectedPR.author.name} wants to merge into{' '}
                      <code>{selectedPR.targetBranch}</code> from{' '}
                      <code>{selectedPR.sourceBranch}</code>
                    </Typography>
                  </Box>
                </Box>
                <Box>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<MergeIcon />}
                    sx={{ mr: 1 }}
                  >
                    Merge
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<CommentIcon />}
                    onClick={() => setShowChat(!showChat)}
                  >
                    {showChat ? 'Hide Discussion' : 'Show Discussion'}
                  </Button>
                </Box>
              </Box>

              <Tabs
                value={activeTab}
                onChange={(_, value) => setActiveTab(value)}
                sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
              >
                <Tab label="Files Changed" />
                <Tab label="Commits" />
                <Tab label="Checks" />
              </Tabs>

              {activeTab === 0 && (
                <Box>
                  {selectedPR.files.map((file, index) => (
                    <Paper
                      key={index}
                      variant="outlined"
                      sx={{ mb: 2, overflow: 'hidden' }}
                    >
                      <Box
                        sx={{
                          p: 1,
                          backgroundColor: 'action.hover',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <Typography variant="subtitle2" sx={{ fontFamily: 'monospace' }}>
                          {file.path}
                        </Typography>
                        <Box>
                          <Chip
                            label={`+${file.additions}`}
                            size="small"
                            color="success"
                            sx={{ mr: 1 }}
                          />
                          <Chip
                            label={`-${file.deletions}`}
                            size="small"
                            color="error"
                          />
                        </Box>
                      </Box>
                      <SyntaxHighlighter
                        language="typescript"
                        style={vscDarkPlus}
                        showLineNumbers
                      >
                        {file.diff}
                      </SyntaxHighlighter>
                    </Paper>
                  ))}
                </Box>
              )}

              {activeTab === 1 && (
                <List>
                  {/* Commits list */}
                  <Typography variant="body2" color="text.secondary">
                    {selectedPR.commits} commits
                  </Typography>
                </List>
              )}

              {activeTab === 2 && (
                <List>
                  {selectedPR.checks.map((check, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {check.status === 'success' ? (
                          <CheckIcon color="success" />
                        ) : check.status === 'failure' ? (
                          <CloseIcon color="error" />
                        ) : (
                          <WarningIcon color="warning" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={check.name}
                        secondary={check.description}
                      />
                    </ListItem>
                  ))}
                </List>
              )}

              {showChat && (
                <Box sx={{ mt: 3 }}>
                  <Divider sx={{ mb: 3 }} />
                  <UnifiedChat
                    onSendMessage={handleSendMessage}
                    showThreads={false}
                    currentAgent={{
                      id: 'code-reviewer',
                      name: 'Code Reviewer',
                      type: 'agent',
                      capabilities: ['code-review', 'suggestions'],
                    }}
                  />
                </Box>
              )}
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Filters Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleFilterClose}
      >
        <MenuItem
          onClick={() => toggleStatusFilter('open')}
          sx={{ display: 'flex', gap: 1 }}
        >
          <GitHubIcon color="primary" />
          Open
        </MenuItem>
        <MenuItem
          onClick={() => toggleStatusFilter('merged')}
          sx={{ display: 'flex', gap: 1 }}
        >
          <MergeIcon color="success" />
          Merged
        </MenuItem>
        <MenuItem
          onClick={() => toggleStatusFilter('closed')}
          sx={{ display: 'flex', gap: 1 }}
        >
          <CloseIcon color="error" />
          Closed
        </MenuItem>
      </Menu>
    </Container>
  );
};

export default PullRequests; 