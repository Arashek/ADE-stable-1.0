import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Box,
  CircularProgress,
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  CloudUpload as PushIcon,
  CloudDownload as PullIcon,
  Merge as MergeIcon,
  Add as AddIcon,
  Commit as CommitIcon,
  BranchIcon,
  History as HistoryIcon,
} from '@mui/icons-material';

interface GitCredentials {
  username: string;
  password: string;
  email: string;
}

interface GitStatus {
  branch: string;
  ahead: number;
  behind: number;
  modified: string[];
  staged: string[];
  untracked: string[];
}

export const GitIntegration: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isConnectDialogOpen, setIsConnectDialogOpen] = useState(false);
  const [isPushDialogOpen, setIsPushDialogOpen] = useState(false);
  const [credentials, setCredentials] = useState<GitCredentials>({
    username: '',
    password: '',
    email: '',
  });
  const [repoUrl, setRepoUrl] = useState('');
  const [commitMessage, setCommitMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [gitStatus, setGitStatus] = useState<GitStatus | null>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleConnectDialogOpen = () => {
    setIsConnectDialogOpen(true);
    handleMenuClose();
  };

  const handlePushDialogOpen = () => {
    setIsPushDialogOpen(true);
    handleMenuClose();
  };

  const handleConnect = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/git/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repoUrl,
          credentials,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to connect to repository');
      }

      await updateGitStatus();
      setIsConnectDialogOpen(false);
    } catch (error) {
      console.error('Error connecting to repository:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePush = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/git/push', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          commitMessage,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to push changes');
      }

      await updateGitStatus();
      setIsPushDialogOpen(false);
      setCommitMessage('');
    } catch (error) {
      console.error('Error pushing changes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateGitStatus = async () => {
    try {
      const response = await fetch('/api/git/status');
      const status: GitStatus = await response.json();
      setGitStatus(status);
    } catch (error) {
      console.error('Error fetching git status:', error);
    }
  };

  const handlePull = async () => {
    setIsLoading(true);
    try {
      await fetch('/api/git/pull', { method: 'POST' });
      await updateGitStatus();
    } catch (error) {
      console.error('Error pulling changes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <IconButton
        onClick={handleMenuOpen}
        color={gitStatus ? 'primary' : 'default'}
        sx={{ position: 'relative' }}
      >
        <GitHubIcon />
        {gitStatus && (gitStatus.ahead > 0 || gitStatus.behind > 0) && (
          <Chip
            size="small"
            label={`${gitStatus.ahead}↑ ${gitStatus.behind}↓`}
            sx={{
              position: 'absolute',
              top: -8,
              right: -8,
              height: 16,
              fontSize: '0.6rem',
            }}
          />
        )}
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleConnectDialogOpen}>
          <ListItemIcon>
            <AddIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Connect Repository" />
        </MenuItem>
        <MenuItem onClick={handlePushDialogOpen} disabled={!gitStatus}>
          <ListItemIcon>
            <PushIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Commit & Push" />
        </MenuItem>
        <MenuItem onClick={handlePull} disabled={!gitStatus}>
          <ListItemIcon>
            <PullIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Pull Changes" />
        </MenuItem>
      </Menu>

      <Dialog open={isConnectDialogOpen} onClose={() => setIsConnectDialogOpen(false)}>
        <DialogTitle>Connect to Repository</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Repository URL"
            fullWidth
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Username"
            fullWidth
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Password/Token"
            type="password"
            fullWidth
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Email"
            fullWidth
            value={credentials.email}
            onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsConnectDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConnect} disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : 'Connect'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={isPushDialogOpen} onClose={() => setIsPushDialogOpen(false)}>
        <DialogTitle>Commit & Push Changes</DialogTitle>
        <DialogContent>
          {gitStatus && (
            <Box mb={2}>
              <Typography variant="subtitle2" gutterBottom>
                Current Branch: {gitStatus.branch}
              </Typography>
              <List dense>
                {gitStatus.modified.length > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <CommitIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Modified Files"
                      secondary={gitStatus.modified.join(', ')}
                    />
                  </ListItem>
                )}
                {gitStatus.staged.length > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <CommitIcon color="success" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Staged Files"
                      secondary={gitStatus.staged.join(', ')}
                    />
                  </ListItem>
                )}
                {gitStatus.untracked.length > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <AddIcon color="info" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Untracked Files"
                      secondary={gitStatus.untracked.join(', ')}
                    />
                  </ListItem>
                )}
              </List>
            </Box>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Commit Message"
            fullWidth
            multiline
            rows={4}
            value={commitMessage}
            onChange={(e) => setCommitMessage(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsPushDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handlePush}
            disabled={isLoading || !commitMessage.trim()}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Commit & Push'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 