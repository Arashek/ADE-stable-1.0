import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  IconButton,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  CreateNewFolder as NewFolderIcon
} from '@mui/icons-material';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
}

interface FileExplorerProps {
  projectId: string;
  onFileSelect: (path: string) => void;
}

const FileExplorer: React.FC<FileExplorerProps> = ({ projectId, onFileSelect }) => {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());
  const [newItemDialog, setNewItemDialog] = useState<{
    open: boolean;
    type: 'file' | 'folder';
    parentPath: string;
  }>({
    open: false,
    type: 'file',
    parentPath: ''
  });
  const [newItemName, setNewItemName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchFiles();
  }, [projectId]);

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/files/${projectId}/list`);
      if (!response.ok) throw new Error('Failed to fetch files');
      const data = await response.json();
      setFiles(data);
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleExpand = (path: string) => {
    const newExpanded = new Set(expandedPaths);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedPaths(newExpanded);
  };

  const handleCreateNewItem = async () => {
    try {
      const response = await fetch(`/api/files/${projectId}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: newItemDialog.parentPath,
          name: newItemName,
          type: newItemDialog.type
        })
      });

      if (!response.ok) throw new Error('Failed to create item');
      
      await fetchFiles();
      setNewItemDialog({ open: false, type: 'file', parentPath: '' });
      setNewItemName('');
    } catch (error) {
      console.error('Error creating new item:', error);
    }
  };

  const handleDeleteItem = async (path: string) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;

    try {
      const response = await fetch(`/api/files/${projectId}/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      });

      if (!response.ok) throw new Error('Failed to delete item');
      
      await fetchFiles();
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  const renderFileNode = (node: FileNode, level: number = 0) => {
    const isExpanded = expandedPaths.has(node.path);
    const hasChildren = node.children && node.children.length > 0;

    return (
      <React.Fragment key={node.path}>
        <ListItem
          sx={{
            pl: level * 2,
            '&:hover': {
              bgcolor: 'action.hover'
            }
          }}
        >
          <ListItemButton
            onClick={() => {
              if (node.type === 'file') {
                onFileSelect(node.path);
              } else {
                handleToggleExpand(node.path);
              }
            }}
          >
            <ListItemIcon>
              {node.type === 'directory' ? <FolderIcon /> : <FileIcon />}
            </ListItemIcon>
            <ListItemText primary={node.name} />
            {node.type === 'directory' && (
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleExpand(node.path);
                }}
              >
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
          </ListItemButton>
          <IconButton
            size="small"
            onClick={() => handleDeleteItem(node.path)}
          >
            <DeleteIcon />
          </IconButton>
        </ListItem>
        {node.type === 'directory' && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {node.children?.map(child => renderFileNode(child, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
        <Typography variant="subtitle1" sx={{ flex: 1 }}>
          Files
        </Typography>
        <IconButton
          size="small"
          onClick={() => setNewItemDialog({ open: true, type: 'folder', parentPath: '' })}
        >
          <NewFolderIcon />
        </IconButton>
        <IconButton
          size="small"
          onClick={() => setNewItemDialog({ open: true, type: 'file', parentPath: '' })}
        >
          <AddIcon />
        </IconButton>
      </Box>
      <List sx={{ flex: 1, overflow: 'auto' }}>
        {files.map(node => renderFileNode(node))}
      </List>

      <Dialog open={newItemDialog.open} onClose={() => setNewItemDialog({ open: false, type: 'file', parentPath: '' })}>
        <DialogTitle>
          Create New {newItemDialog.type === 'file' ? 'File' : 'Folder'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewItemDialog({ open: false, type: 'file', parentPath: '' })}>
            Cancel
          </Button>
          <Button onClick={handleCreateNewItem} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileExplorer; 