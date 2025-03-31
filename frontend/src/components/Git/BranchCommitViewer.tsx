import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Menu,
  MenuItem,
  Tooltip,
  InputAdornment,
  LinearProgress,
  Alert,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  AccountTree as BranchIcon,
  Commit as CommitIcon,
  Create as CreateIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Checkout as CheckoutIcon,
  Merge as MergeIcon,
  Compare as CompareIcon,
  History as HistoryIcon,
  Search as SearchIcon,
  Push as PushIcon,
  Pull as PullIcon,
  Rebase as RebaseIcon,
  Reset as ResetIcon,
  Tag as TagIcon,
  Stash as StashIcon,
} from '@mui/icons-material';

interface Commit {
  id: string;
  message: string;
  author: {
    name: string;
    email: string;
  };
  timestamp: string;
  branch: string;
  parentIds: string[];
}

interface Branch {
  name: string;
  commit: string;
  isRemote: boolean;
  isCurrent: boolean;
  ahead: number;
  behind: number;
}

interface BranchCommitViewerProps {
  branches: Branch[];
  commits: Commit[];
  onCheckout: (branchName: string) => void;
  onCreateBranch: (name: string, fromCommit: string) => void;
  onDeleteBranch: (branchName: string) => void;
  onMerge: (sourceBranch: string, targetBranch: string) => void;
  onCompare: (commit1: string, commit2: string) => void;
  onPush: (branchName: string) => void;
  onPull: (branchName: string) => void;
  onRebase: (sourceBranch: string, targetBranch: string) => void;
  onReset: (commitId: string, type: 'soft' | 'mixed' | 'hard') => void;
  onCreateTag: (commitId: string, tagName: string) => void;
  onStash: (message?: string) => void;
  onApplyStash: (stashId: string) => void;
  isLoading?: boolean;
}

const BranchCommitViewer: React.FC<BranchCommitViewerProps> = ({
  branches,
  commits,
  onCheckout,
  onCreateBranch,
  onDeleteBranch,
  onMerge,
  onCompare,
  onPush,
  onPull,
  onRebase,
  onReset,
  onCreateTag,
  onStash,
  onApplyStash,
  isLoading = false,
}) => {
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null);
  const [selectedCommit, setSelectedCommit] = useState<Commit | null>(null);
  const [createBranchDialogOpen, setCreateBranchDialogOpen] = useState(false);
  const [newBranchName, setNewBranchName] = useState('');
  const [branchMenuAnchorEl, setBranchMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [commitMenuAnchorEl, setCommitMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [stashDialogOpen, setStashDialogOpen] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [stashMessage, setStashMessage] = useState('');
  const [resetType, setResetType] = useState<'soft' | 'mixed' | 'hard'>('soft');

  // Filter commits based on search query
  const filteredCommits = useMemo(() => {
    if (!searchQuery) return commits;
    const query = searchQuery.toLowerCase();
    return commits.filter(
      (commit) =>
        commit.message.toLowerCase().includes(query) ||
        commit.author.name.toLowerCase().includes(query) ||
        commit.id.toLowerCase().includes(query)
    );
  }, [commits, searchQuery]);

  const handleBranchClick = (branchName: string) => {
    setSelectedBranch(branchName);
    setSelectedCommit(null);
  };

  const handleCommitClick = (commit: Commit) => {
    setSelectedCommit(commit);
    setSelectedBranch(null);
  };

  const handleCreateBranch = () => {
    if (selectedCommit && newBranchName.trim()) {
      onCreateBranch(newBranchName.trim(), selectedCommit.id);
      setCreateBranchDialogOpen(false);
      setNewBranchName('');
    }
  };

  const handleBranchMenuClick = (event: React.MouseEvent<HTMLElement>, branchName: string) => {
    setSelectedBranch(branchName);
    setBranchMenuAnchorEl(event.currentTarget);
  };

  const handleCommitMenuClick = (event: React.MouseEvent<HTMLElement>, commit: Commit) => {
    setSelectedCommit(commit);
    setCommitMenuAnchorEl(event.currentTarget);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const handleReset = () => {
    if (selectedCommit) {
      onReset(selectedCommit.id, resetType);
      setResetDialogOpen(false);
    }
  };

  const handleCreateTag = () => {
    if (selectedCommit && newTagName.trim()) {
      onCreateTag(selectedCommit.id, newTagName.trim());
      setTagDialogOpen(false);
      setNewTagName('');
    }
  };

  const handleStash = () => {
    onStash(stashMessage.trim());
    setStashDialogOpen(false);
    setStashMessage('');
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Git History</Typography>
          <Box>
            <Tooltip title="Stash Changes">
              <IconButton onClick={() => setStashDialogOpen(true)} sx={{ mr: 1 }}>
                <StashIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Push Changes">
              <IconButton onClick={() => selectedBranch && onPush(selectedBranch)} sx={{ mr: 1 }}>
                <PushIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Pull Changes">
              <IconButton onClick={() => selectedBranch && onPull(selectedBranch)}>
                <PullIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        <TextField
          fullWidth
          size="small"
          placeholder="Search commits..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {isLoading && <LinearProgress />}

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Branches Panel */}
        <Paper sx={{ width: 250, borderRight: 1, borderColor: 'divider' }}>
          <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="subtitle2">Branches</Typography>
            <IconButton size="small" onClick={() => setCreateBranchDialogOpen(true)}>
              <CreateIcon />
            </IconButton>
          </Box>
          <List>
            {branches.map((branch) => (
              <ListItem
                key={branch.name}
                button
                selected={selectedBranch === branch.name}
                onClick={() => handleBranchClick(branch.name)}
              >
                <ListItemIcon>
                  <BranchIcon color={branch.isCurrent ? 'primary' : 'inherit'} />
                </ListItemIcon>
                <ListItemText
                  primary={branch.name}
                  secondary={
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {branch.ahead > 0 && (
                        <Chip
                          label={`+${branch.ahead}`}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      )}
                      {branch.behind > 0 && (
                        <Chip
                          label={`-${branch.behind}`}
                          size="small"
                          color="error"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={(e) => handleBranchMenuClick(e, branch.name)}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>

        {/* Commits Panel */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          <List>
            {filteredCommits.map((commit) => (
              <React.Fragment key={commit.id}>
                <ListItem
                  button
                  selected={selectedCommit?.id === commit.id}
                  onClick={() => handleCommitClick(commit)}
                >
                  <ListItemIcon>
                    <CommitIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={commit.message}
                    secondary={
                      <Box>
                        <Typography variant="caption" component="span">
                          {commit.author.name} · {formatTimestamp(commit.timestamp)}
                        </Typography>
                        <Chip
                          label={commit.branch}
                          size="small"
                          sx={{ ml: 1 }}
                          variant="outlined"
                        />
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => handleCommitMenuClick(e, commit)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </Box>
      </Box>

      {/* Branch Menu */}
      <Menu
        anchorEl={branchMenuAnchorEl}
        open={Boolean(branchMenuAnchorEl)}
        onClose={() => setBranchMenuAnchorEl(null)}
      >
        <MenuItem onClick={() => {
          if (selectedBranch) {
            onCheckout(selectedBranch);
            setBranchMenuAnchorEl(null);
          }
        }}>
          <CheckoutIcon sx={{ mr: 1 }} /> Checkout
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedBranch) {
            onDeleteBranch(selectedBranch);
            setBranchMenuAnchorEl(null);
          }
        }}>
          <DeleteIcon sx={{ mr: 1 }} /> Delete
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedBranch) {
            onRebase(selectedBranch, 'main');
            setBranchMenuAnchorEl(null);
          }
        }}>
          <RebaseIcon sx={{ mr: 1 }} /> Rebase onto main
        </MenuItem>
      </Menu>

      {/* Commit Menu */}
      <Menu
        anchorEl={commitMenuAnchorEl}
        open={Boolean(commitMenuAnchorEl)}
        onClose={() => setCommitMenuAnchorEl(null)}
      >
        <MenuItem onClick={() => {
          if (selectedCommit) {
            setCreateBranchDialogOpen(true);
            setCommitMenuAnchorEl(null);
          }
        }}>
          <CreateIcon sx={{ mr: 1 }} /> Create Branch
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedCommit) {
            onCompare(selectedCommit.id, selectedCommit.parentIds[0]);
            setCommitMenuAnchorEl(null);
          }
        }}>
          <CompareIcon sx={{ mr: 1 }} /> Compare with Parent
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedCommit) {
            setTagDialogOpen(true);
            setCommitMenuAnchorEl(null);
          }
        }}>
          <TagIcon sx={{ mr: 1 }} /> Create Tag
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedCommit) {
            setResetDialogOpen(true);
            setCommitMenuAnchorEl(null);
          }
        }}>
          <ResetIcon sx={{ mr: 1 }} /> Reset to this commit
        </MenuItem>
      </Menu>

      {/* Create Branch Dialog */}
      <Dialog
        open={createBranchDialogOpen}
        onClose={() => setCreateBranchDialogOpen(false)}
      >
        <DialogTitle>Create New Branch</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Branch Name"
            fullWidth
            value={newBranchName}
            onChange={(e) => setNewBranchName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateBranchDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateBranch} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Dialog */}
      <Dialog
        open={resetDialogOpen}
        onClose={() => setResetDialogOpen(false)}
      >
        <DialogTitle>Reset to Commit</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Choose reset type:
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={resetType === 'soft'}
                onChange={() => setResetType('soft')}
              />
            }
            label="Soft (keep changes staged)"
          />
          <FormControlLabel
            control={
              <Switch
                checked={resetType === 'mixed'}
                onChange={() => setResetType('mixed')}
              />
            }
            label="Mixed (keep changes unstaged)"
          />
          <FormControlLabel
            control={
              <Switch
                checked={resetType === 'hard'}
                onChange={() => setResetType('hard')}
              />
            }
            label="Hard (discard all changes)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleReset} color="error" variant="contained">
            Reset
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Tag Dialog */}
      <Dialog
        open={tagDialogOpen}
        onClose={() => setTagDialogOpen(false)}
      >
        <DialogTitle>Create Tag</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Tag Name"
            fullWidth
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTagDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateTag} variant="contained">
            Create Tag
          </Button>
        </DialogActions>
      </Dialog>

      {/* Stash Dialog */}
      <Dialog
        open={stashDialogOpen}
        onClose={() => setStashDialogOpen(false)}
      >
        <DialogTitle>Stash Changes</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Stash Message (optional)"
            fullWidth
            value={stashMessage}
            onChange={(e) => setStashMessage(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStashDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleStash} variant="contained">
            Stash Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BranchCommitViewer; 