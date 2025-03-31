import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Breadcrumbs,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Folder,
  InsertDriveFile,
  Upload,
  Download,
  Delete,
  MoreVert,
  CreateNewFolder,
  Edit,
} from '@mui/icons-material';
import { ContainerService } from '../../services/ContainerService';

interface ContainerFileBrowserProps {
  containerId: string;
  containerName: string;
}

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
}

export const ContainerFileBrowser: React.FC<ContainerFileBrowserProps> = ({
  containerId,
  containerName,
}) => {
  const [currentPath, setCurrentPath] = useState('/');
  const [files, setFiles] = useState<FileItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    file: FileItem;
  } | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createType, setCreateType] = useState<'file' | 'directory'>('file');
  const [newItemName, setNewItemName] = useState('');
  const containerService = new ContainerService();

  useEffect(() => {
    loadFiles();
  }, [currentPath]);

  const loadFiles = async () => {
    try {
      const fileList = await containerService.listFiles(containerId, currentPath);
      setFiles(fileList);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const handleFileClick = (file: FileItem) => {
    if (file.type === 'directory') {
      setCurrentPath(file.path);
    } else {
      // Handle file click (e.g., open in editor)
      console.log('File clicked:', file);
    }
  };

  const handleContextMenu = (event: React.MouseEvent, file: FileItem) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX,
      mouseY: event.clientY,
      file,
    });
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
  };

  const handleCreateItem = async () => {
    try {
      if (createType === 'directory') {
        await containerService.createDirectory(containerId, `${currentPath}${newItemName}`);
      } else {
        await containerService.createFile(containerId, `${currentPath}${newItemName}`);
      }
      setCreateDialogOpen(false);
      setNewItemName('');
      loadFiles();
    } catch (error) {
      console.error('Failed to create item:', error);
    }
  };

  const handleDeleteItem = async (file: FileItem) => {
    try {
      await containerService.deleteFile(containerId, file.path);
      loadFiles();
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const handleDownloadFile = async (file: FileItem) => {
    try {
      await containerService.downloadFile(containerId, file.path);
    } catch (error) {
      console.error('Failed to download file:', error);
    }
  };

  const handleUploadFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      await containerService.uploadFile(containerId, currentPath, file);
      loadFiles();
    } catch (error) {
      console.error('Failed to upload file:', error);
    }
  };

  const formatFileSize = (size?: number) => {
    if (!size) return '';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let index = 0;
    while (size >= 1024 && index < units.length - 1) {
      size /= 1024;
      index++;
    }
    return `${size.toFixed(1)} ${units[index]}`;
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" gutterBottom>
          File Browser - {containerName}
        </Typography>
        <Breadcrumbs>
          <Link
            component="button"
            variant="body1"
            onClick={() => setCurrentPath('/')}
          >
            Root
          </Link>
          {currentPath
            .split('/')
            .filter(Boolean)
            .map((segment, index, array) => (
              <Link
                key={index}
                component="button"
                variant="body1"
                onClick={() =>
                  setCurrentPath('/' + array.slice(0, index + 1).join('/'))
                }
              >
                {segment}
              </Link>
            ))}
        </Breadcrumbs>
      </Box>

      <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
        <Button
          variant="outlined"
          startIcon={<CreateNewFolder />}
          onClick={() => {
            setCreateType('directory');
            setCreateDialogOpen(true);
          }}
        >
          New Folder
        </Button>
        <Button
          variant="outlined"
          startIcon={<Upload />}
          component="label"
        >
          Upload File
          <input
            type="file"
            hidden
            onChange={handleUploadFile}
          />
        </Button>
      </Box>

      <Paper sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List>
          {files.map((file) => (
            <ListItem
              key={file.path}
              button
              onClick={() => handleFileClick(file)}
              onContextMenu={(e) => handleContextMenu(e, file)}
            >
              <ListItemIcon>
                {file.type === 'directory' ? <Folder /> : <InsertDriveFile />}
              </ListItemIcon>
              <ListItemText
                primary={file.name}
                secondary={
                  file.type === 'file'
                    ? `${formatFileSize(file.size)} • ${new Date(
                        file.modified || ''
                      ).toLocaleString()}`
                    : undefined
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={(e) => {
                    e.stopPropagation();
                    setContextMenu({
                      mouseX: e.clientX,
                      mouseY: e.clientY,
                      file,
                    });
                  }}
                >
                  <MoreVert />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Menu
        open={contextMenu !== null}
        onClose={handleContextMenuClose}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        {contextMenu?.file.type === 'file' && (
          <>
            <MenuItem onClick={() => handleDownloadFile(contextMenu.file)}>
              <Download sx={{ mr: 1 }} /> Download
            </MenuItem>
            <MenuItem onClick={() => handleDeleteItem(contextMenu.file)}>
              <Delete sx={{ mr: 1 }} /> Delete
            </MenuItem>
          </>
        )}
        {contextMenu?.file.type === 'directory' && (
          <MenuItem onClick={() => handleDeleteItem(contextMenu.file)}>
            <Delete sx={{ mr: 1 }} /> Delete
          </MenuItem>
        )}
      </Menu>

      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>
          Create New {createType === 'file' ? 'File' : 'Directory'}
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
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateItem} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 