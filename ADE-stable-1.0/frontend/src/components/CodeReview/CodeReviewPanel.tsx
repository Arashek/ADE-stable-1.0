import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Chip,
  TextField,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Check as ApproveIcon,
  Close as RejectIcon,
  Comment as CommentIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeComment {
  id: string;
  content: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
  };
  lineNumber: number;
  createdAt: string;
  status: 'open' | 'resolved';
  replies: CodeComment[];
}

interface CodeChange {
  path: string;
  oldContent: string;
  newContent: string;
  type: 'added' | 'modified' | 'deleted';
  hunks: Array<{
    oldStart: number;
    oldLines: number;
    newStart: number;
    newLines: number;
    content: string;
  }>;
}

interface CodeReviewPanelProps {
  pullRequestId: string;
  changes: CodeChange[];
  comments: CodeComment[];
  onAddComment: (comment: Omit<CodeComment, 'id' | 'createdAt'>) => void;
  onResolveComment: (commentId: string) => void;
  onUpdateComment: (commentId: string, content: string) => void;
  onDeleteComment: (commentId: string) => void;
  onApproveChanges: () => void;
  onRequestChanges: (feedback: string) => void;
}

const CodeReviewPanel: React.FC<CodeReviewPanelProps> = ({
  pullRequestId,
  changes,
  comments,
  onAddComment,
  onResolveComment,
  onUpdateComment,
  onDeleteComment,
  onApproveChanges,
  onRequestChanges,
}) => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [newComment, setNewComment] = useState('');
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedComment, setSelectedComment] = useState<CodeComment | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [requestChangesDialogOpen, setRequestChangesDialogOpen] = useState(false);
  const [changeFeedback, setChangeFeedback] = useState('');

  useEffect(() => {
    if (changes.length > 0) {
      setSelectedFile(changes[0].path);
    }
  }, [changes]);

  const handleCommentSubmit = () => {
    if (!newComment.trim() || !selectedLine) return;

    onAddComment({
      content: newComment,
      author: {
        id: 'current-user',
        name: 'Current User',
      },
      lineNumber: selectedLine,
      status: 'open',
      replies: [],
    });

    setNewComment('');
    setSelectedLine(null);
  };

  const handleCommentAction = (action: 'edit' | 'delete') => {
    if (!selectedComment) return;

    if (action === 'edit') {
      setEditContent(selectedComment.content);
      setEditDialogOpen(true);
    } else {
      onDeleteComment(selectedComment.id);
    }
    setMenuAnchorEl(null);
  };

  const handleEditSubmit = () => {
    if (!selectedComment || !editContent.trim()) return;
    onUpdateComment(selectedComment.id, editContent);
    setEditDialogOpen(false);
    setEditContent('');
  };

  const handleRequestChangesSubmit = () => {
    if (!changeFeedback.trim()) return;
    onRequestChanges(changeFeedback);
    setRequestChangesDialogOpen(false);
    setChangeFeedback('');
  };

  const renderFileContent = () => {
    const currentFile = changes.find((change) => change.path === selectedFile);
    if (!currentFile) return null;

    const fileComments = comments.filter(
      (comment) => comment.lineNumber >= 0
    );

    return (
      <Box>
        <Paper variant="outlined" sx={{ mb: 2 }}>
          <Box sx={{ p: 1, backgroundColor: 'action.hover' }}>
            <Typography variant="subtitle2" sx={{ fontFamily: 'monospace' }}>
              {currentFile.path}
            </Typography>
          </Box>
          <Box sx={{ position: 'relative' }}>
            {currentFile.hunks.map((hunk, hunkIndex) => (
              <Box key={hunkIndex}>
                <Box sx={{ backgroundColor: 'action.hover', px: 1, py: 0.5 }}>
                  <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                    @@ -{hunk.oldStart},{hunk.oldLines} +{hunk.newStart},{hunk.newLines} @@
                  </Typography>
                </Box>
                <SyntaxHighlighter
                  language="typescript"
                  style={vscDarkPlus}
                  showLineNumbers
                  startingLineNumber={hunk.newStart}
                  wrapLines
                  lineProps={(lineNumber) => ({
                    style: {
                      cursor: 'pointer',
                      backgroundColor:
                        selectedLine === lineNumber
                          ? 'rgba(62, 175, 255, 0.1)'
                          : undefined,
                    },
                    onClick: () => setSelectedLine(lineNumber),
                  })}
                >
                  {hunk.content}
                </SyntaxHighlighter>
              </Box>
            ))}
          </Box>
        </Paper>

        {/* Comments Section */}
        <Box sx={{ ml: 2 }}>
          {fileComments.map((comment) => (
            <Paper key={comment.id} sx={{ mb: 2, p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Avatar src={comment.author.avatar} sx={{ mr: 1 }}>
                  {comment.author.name[0]}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2">
                    {comment.author.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Line {comment.lineNumber} · {new Date(comment.createdAt).toLocaleString()}
                  </Typography>
                </Box>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    setSelectedComment(comment);
                    setMenuAnchorEl(e.currentTarget);
                  }}
                >
                  <MoreVertIcon />
                </IconButton>
              </Box>
              <Typography>{comment.content}</Typography>
              {comment.status === 'open' && (
                <Button
                  size="small"
                  startIcon={<ApproveIcon />}
                  onClick={() => onResolveComment(comment.id)}
                  sx={{ mt: 1 }}
                >
                  Resolve
                </Button>
              )}
            </Paper>
          ))}
        </Box>

        {/* New Comment Input */}
        {selectedLine && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="caption" sx={{ mb: 1, display: 'block' }}>
              Adding comment for line {selectedLine}
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              variant="outlined"
              size="small"
              sx={{ mb: 1 }}
            />
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button onClick={() => setSelectedLine(null)}>Cancel</Button>
              <Button
                variant="contained"
                onClick={handleCommentSubmit}
                disabled={!newComment.trim()}
              >
                Submit
              </Button>
            </Box>
          </Paper>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="h6">Code Review</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            color="error"
            startIcon={<RejectIcon />}
            onClick={() => setRequestChangesDialogOpen(true)}
          >
            Request Changes
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<ApproveIcon />}
            onClick={onApproveChanges}
          >
            Approve
          </Button>
        </Box>
      </Box>

      {/* File List */}
      <Box sx={{ display: 'flex', height: 'calc(100% - 64px)' }}>
        <Paper
          sx={{
            width: 250,
            borderRight: 1,
            borderColor: 'divider',
            overflowY: 'auto',
          }}
        >
          <List>
            {changes.map((change) => (
              <ListItem
                key={change.path}
                button
                selected={selectedFile === change.path}
                onClick={() => setSelectedFile(change.path)}
              >
                <ListItemText
                  primary={change.path.split('/').pop()}
                  secondary={change.path}
                  secondaryTypographyProps={{
                    sx: { fontSize: '0.75rem', overflow: 'hidden', textOverflow: 'ellipsis' },
                  }}
                />
                <Chip
                  label={change.type}
                  size="small"
                  color={
                    change.type === 'added'
                      ? 'success'
                      : change.type === 'deleted'
                      ? 'error'
                      : 'primary'
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>

        {/* File Content and Comments */}
        <Box sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
          {renderFileContent()}
        </Box>
      </Box>

      {/* Comment Actions Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={() => setMenuAnchorEl(null)}
      >
        <MenuItem onClick={() => handleCommentAction('edit')}>
          <EditIcon sx={{ mr: 1 }} /> Edit
        </MenuItem>
        <MenuItem
          onClick={() => handleCommentAction('delete')}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>

      {/* Edit Comment Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
      >
        <DialogTitle>Edit Comment</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleEditSubmit}
            disabled={!editContent.trim()}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Request Changes Dialog */}
      <Dialog
        open={requestChangesDialogOpen}
        onClose={() => setRequestChangesDialogOpen(false)}
      >
        <DialogTitle>Request Changes</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={changeFeedback}
            onChange={(e) => setChangeFeedback(e.target.value)}
            placeholder="Describe the changes needed..."
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestChangesDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleRequestChangesSubmit}
            disabled={!changeFeedback.trim()}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CodeReviewPanel; 