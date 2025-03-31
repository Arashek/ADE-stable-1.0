import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Badge,
  CircularProgress,
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  CloudUpload as PushIcon,
  CloudDownload as PullIcon,
  Merge as MergeIcon,
  BranchIcon,
  Sync as SyncIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface GitStatus {
  branch: string;
  ahead: number;
  behind: number;
  modified: number;
  staged: number;
  conflicts: number;
  isClean: boolean;
}

interface GitStatusBarProps {
  onPush: () => Promise<void>;
  onPull: () => Promise<void>;
  onSync: () => Promise<void>;
  onBranchChange: (branch: string) => Promise<void>;
}

export const GitStatusBar: React.FC<GitStatusBarProps> = ({
  onPush,
  onPull,
  onSync,
  onBranchChange,
}) => {
  const theme = useTheme();
  const [status, setStatus] = useState<GitStatus>({
    branch: 'main',
    ahead: 0,
    behind: 0,
    modified: 0,
    staged: 0,
    conflicts: 0,
    isClean: true,
  });
  const [loading, setLoading] = useState(false);
  const [branchMenuAnchor, setBranchMenuAnchor] = useState<null | HTMLElement>(null);
  const [branches, setBranches] = useState<string[]>([]);

  useEffect(() => {
    // Mock fetching branches
    setBranches(['main', 'develop', 'feature/new-ui']);
  }, []);

  const handleSync = async () => {
    setLoading(true);
    try {
      await onSync();
    } finally {
      setLoading(false);
    }
  };

  const handlePush = async () => {
    setLoading(true);
    try {
      await onPush();
    } finally {
      setLoading(false);
    }
  };

  const handlePull = async () => {
    setLoading(true);
    try {
      await onPull();
    } finally {
      setLoading(false);
    }
  };

  const handleBranchSelect = async (branch: string) => {
    setBranchMenuAnchor(null);
    setLoading(true);
    try {
      await onBranchChange(branch);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        padding: '4px 8px',
        borderTop: `1px solid ${theme.palette.divider}`,
        backgroundColor: theme.palette.background.paper,
      }}
    >
      <Tooltip title="Git">
        <IconButton size="small">
          <GitHubIcon fontSize="small" />
        </IconButton>
      </Tooltip>

      <Tooltip title="Current Branch">
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            '&:hover': { opacity: 0.8 },
          }}
          onClick={(e) => setBranchMenuAnchor(e.currentTarget)}
        >
          <BranchIcon fontSize="small" sx={{ mr: 0.5 }} />
          <Typography variant="body2">
            {status.branch}
          </Typography>
        </Box>
      </Tooltip>

      <Menu
        anchorEl={branchMenuAnchor}
        open={Boolean(branchMenuAnchor)}
        onClose={() => setBranchMenuAnchor(null)}
      >
        {branches.map(branch => (
          <MenuItem
            key={branch}
            onClick={() => handleBranchSelect(branch)}
            selected={branch === status.branch}
          >
            {branch}
          </MenuItem>
        ))}
      </Menu>

      {loading ? (
        <CircularProgress size={20} />
      ) : (
        <>
          {(status.ahead > 0 || status.behind > 0) && (
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {status.ahead > 0 && `↑${status.ahead}`}
              {status.behind > 0 && `↓${status.behind}`}
            </Typography>
          )}

          <Tooltip title="Sync">
            <IconButton size="small" onClick={handleSync}>
              <SyncIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Push">
            <IconButton
              size="small"
              onClick={handlePush}
              disabled={status.ahead === 0}
            >
              <Badge badgeContent={status.ahead} color="primary">
                <PushIcon fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>

          <Tooltip title="Pull">
            <IconButton
              size="small"
              onClick={handlePull}
              disabled={status.behind === 0}
            >
              <Badge badgeContent={status.behind} color="warning">
                <PullIcon fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>

          {status.conflicts > 0 && (
            <Tooltip title={`${status.conflicts} conflicts`}>
              <IconButton size="small" color="error">
                <Badge badgeContent={status.conflicts} color="error">
                  <MergeIcon fontSize="small" />
                </Badge>
              </IconButton>
            </Tooltip>
          )}

          {!status.isClean && (
            <Typography
              variant="body2"
              sx={{
                color: status.conflicts > 0 ? 'error.main' : 'warning.main',
              }}
            >
              {status.modified} changed
              {status.staged > 0 && `, ${status.staged} staged`}
            </Typography>
          )}
        </>
      )}
    </Box>
  );
};
