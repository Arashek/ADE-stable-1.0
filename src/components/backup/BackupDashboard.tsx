import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert
} from '@mui/material';
import {
  Backup as BackupIcon,
  Restore as RestoreIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import { BackupMetadata } from '../../core/backup/BackupManager';

interface BackupDashboardProps {
  onRefresh: () => Promise<void>;
  onBackup: (type: 'container' | 'project', tags?: string[]) => Promise<void>;
  onRestore: (backupId: string) => Promise<void>;
  onDelete: (backupId: string) => Promise<void>;
  backups: BackupMetadata[];
  activeBackups: string[];
  activeRestores: string[];
  error?: string;
}

export const BackupDashboard: React.FC<BackupDashboardProps> = ({
  onRefresh,
  onBackup,
  onRestore,
  onDelete,
  backups,
  activeBackups,
  activeRestores,
  error
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<BackupMetadata | null>(null);
  const [isRestoreDialogOpen, setIsRestoreDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isBackupDialogOpen, setIsBackupDialogOpen] = useState(false);
  const [backupType, setBackupType] = useState<'container' | 'project'>('container');
  const [backupTags, setBackupTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await onRefresh();
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackup = async () => {
    setIsLoading(true);
    try {
      await onBackup(backupType, backupTags);
      setIsBackupDialogOpen(false);
      setBackupTags([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestore = async () => {
    if (!selectedBackup) return;
    setIsLoading(true);
    try {
      await onRestore(selectedBackup.id);
      setIsRestoreDialogOpen(false);
      setSelectedBackup(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedBackup) return;
    setIsLoading(true);
    try {
      await onDelete(selectedBackup.id);
      setIsDeleteDialogOpen(false);
      setSelectedBackup(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTag = () => {
    if (newTag && !backupTags.includes(newTag)) {
      setBackupTags([...backupTags, newTag]);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setBackupTags(backupTags.filter(t => t !== tag));
  };

  const getStatusColor = (status: BackupMetadata['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'in_progress':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Backups
              </Typography>
              <Typography variant="h4">
                {backups.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Backups
              </Typography>
              <Typography variant="h4">
                {activeBackups.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Restores
              </Typography>
              <Typography variant="h4">
                {activeRestores.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<BackupIcon />}
              onClick={() => setIsBackupDialogOpen(true)}
              disabled={isLoading}
            >
              Create Backup
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleRefresh}
              disabled={isLoading}
            >
              Refresh
            </Button>
          </Box>
        </Grid>

        {/* Backups Table */}
        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Tags</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {backups.map((backup) => (
                  <TableRow key={backup.id}>
                    <TableCell>{backup.id}</TableCell>
                    <TableCell>{backup.type}</TableCell>
                    <TableCell>
                      <Chip
                        label={backup.status}
                        color={getStatusColor(backup.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {(backup.size / 1024 / 1024).toFixed(2)} MB
                    </TableCell>
                    <TableCell>
                      {format(new Date(backup.timestamp), 'PPpp')}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {backup.tags?.map((tag) => (
                          <Chip
                            key={tag}
                            label={tag}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        color="primary"
                        onClick={() => {
                          setSelectedBackup(backup);
                          setIsRestoreDialogOpen(true);
                        }}
                        disabled={backup.status !== 'completed'}
                      >
                        <RestoreIcon />
                      </IconButton>
                      <IconButton
                        color="error"
                        onClick={() => {
                          setSelectedBackup(backup);
                          setIsDeleteDialogOpen(true);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>

      {/* Backup Dialog */}
      <Dialog open={isBackupDialogOpen} onClose={() => setIsBackupDialogOpen(false)}>
        <DialogTitle>Create Backup</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            label="Backup Type"
            value={backupType}
            onChange={(e) => setBackupType(e.target.value as 'container' | 'project')}
            sx={{ mt: 2 }}
          >
            <MenuItem value="container">Container</MenuItem>
            <MenuItem value="project">Project</MenuItem>
          </TextField>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Tags
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <TextField
                size="small"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add tag"
              />
              <Button onClick={handleAddTag}>Add</Button>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {backupTags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onDelete={() => handleRemoveTag(tag)}
                />
              ))}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsBackupDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleBackup}
            disabled={isLoading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Restore Dialog */}
      <Dialog open={isRestoreDialogOpen} onClose={() => setIsRestoreDialogOpen(false)}>
        <DialogTitle>Restore Backup</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to restore this backup? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsRestoreDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleRestore}
            disabled={isLoading}
          >
            Restore
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete Backup</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this backup? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDelete}
            disabled={isLoading}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Loading Progress */}
      {isLoading && (
        <LinearProgress sx={{ position: 'fixed', top: 0, left: 0, right: 0 }} />
      )}
    </Box>
  );
}; 