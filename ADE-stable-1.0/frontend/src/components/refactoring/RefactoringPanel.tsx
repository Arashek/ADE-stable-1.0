import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Divider,
  Button,
  TextField,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Code as RefactorIcon,
  Functions as ExtractMethodIcon,
  Label as RenameIcon,
  Add as ExtractVariableIcon,
  Remove as InlineVariableIcon,
  SwapHoriz as MoveIcon,
  CompareArrows as CompareIcon,
  Preview as PreviewIcon,
  Undo as UndoIcon,
  Redo as RedoIcon
} from '@mui/icons-material';

interface RefactoringOperation {
  id: string;
  type: string;
  description: string;
  file: string;
  line: number;
  preview?: string;
  status: 'pending' | 'applied' | 'failed';
  error?: string;
}

interface RefactoringHistory {
  operations: RefactoringOperation[];
  currentIndex: number;
}

interface RefactoringPanelProps {
  onApplyRefactoring: (operation: RefactoringOperation) => void;
  onPreviewRefactoring: (operation: RefactoringOperation) => void;
  onUndo: () => void;
  onRedo: () => void;
}

const REFACTORING_TYPES = [
  {
    id: 'extract-method',
    name: 'Extract Method',
    description: 'Extract selected code into a new method',
    icon: ExtractMethodIcon
  },
  {
    id: 'rename-symbol',
    name: 'Rename Symbol',
    description: 'Rename a variable, function, or class',
    icon: RenameIcon
  },
  {
    id: 'extract-variable',
    name: 'Extract Variable',
    description: 'Extract expression into a new variable',
    icon: ExtractVariableIcon
  },
  {
    id: 'inline-variable',
    name: 'Inline Variable',
    description: 'Replace variable usage with its value',
    icon: InlineVariableIcon
  },
  {
    id: 'move-method',
    name: 'Move Method',
    description: 'Move a method to another class',
    icon: MoveIcon
  },
  {
    id: 'change-signature',
    name: 'Change Signature',
    description: 'Modify method parameters and return type',
    icon: CompareIcon
  }
];

const RefactoringPanel: React.FC<RefactoringPanelProps> = ({
  onApplyRefactoring,
  onPreviewRefactoring,
  onUndo,
  onRedo
}) => {
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedOperation, setSelectedOperation] = useState<RefactoringOperation | null>(null);
  const [history, setHistory] = useState<RefactoringHistory>({
    operations: [],
    currentIndex: -1
  });
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [previewContent, setPreviewContent] = useState<string>('');

  const handleTypeSelect = (type: string) => {
    setSelectedType(type);
    const operation: RefactoringOperation = {
      id: Date.now().toString(),
      type,
      description: REFACTORING_TYPES.find(t => t.id === type)?.description || '',
      file: 'current-file.ts', // This should come from the editor context
      line: 1, // This should come from the editor context
      status: 'pending'
    };
    setSelectedOperation(operation);
  };

  const handlePreview = async () => {
    if (!selectedOperation) return;
    
    setIsPreviewing(true);
    try {
      await onPreviewRefactoring(selectedOperation);
      // Simulate preview content
      setPreviewContent('// Preview of refactored code\nfunction newMethod() {\n  // Extracted code\n}');
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleApply = async () => {
    if (!selectedOperation) return;

    try {
      await onApplyRefactoring(selectedOperation);
      setHistory(prev => ({
        operations: [...prev.operations.slice(0, prev.currentIndex + 1), selectedOperation],
        currentIndex: prev.currentIndex + 1
      }));
      setSelectedOperation(null);
      setSelectedType('');
    } catch (error) {
      setSelectedOperation(prev => prev ? {
        ...prev,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      } : null);
    }
  };

  const handleUndo = () => {
    onUndo();
    setHistory(prev => ({
      ...prev,
      currentIndex: Math.max(0, prev.currentIndex - 1)
    }));
  };

  const handleRedo = () => {
    onRedo();
    setHistory(prev => ({
      ...prev,
      currentIndex: Math.min(prev.operations.length - 1, prev.currentIndex + 1)
    }));
  };

  const canUndo = history.currentIndex > 0;
  const canRedo = history.currentIndex < history.operations.length - 1;

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 1 }}>
        <RefactorIcon color="primary" />
        <Typography variant="h6" sx={{ flex: 1 }}>Refactoring</Typography>
        <Tooltip title="Undo">
          <IconButton onClick={handleUndo} disabled={!canUndo}>
            <UndoIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Redo">
          <IconButton onClick={handleRedo} disabled={!canRedo}>
            <RedoIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom>Available Refactorings</Typography>
          <Grid container spacing={2}>
            {REFACTORING_TYPES.map(type => {
              const Icon = type.icon;
              return (
                <Grid item xs={12} sm={6} md={4} key={type.id}>
                  <Paper
                    sx={{
                      p: 2,
                      cursor: 'pointer',
                      bgcolor: selectedType === type.id ? 'action.selected' : 'background.paper',
                      '&:hover': {
                        bgcolor: 'action.hover'
                      }
                    }}
                    onClick={() => handleTypeSelect(type.id)}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Icon color="primary" />
                      <Typography variant="subtitle1">{type.name}</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {type.description}
                    </Typography>
                  </Paper>
                </Grid>
              );
            })}
          </Grid>
        </Box>

        {selectedOperation && (
          <>
            <Divider />
            <Box sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Refactoring Details</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    value={selectedOperation.description}
                    disabled
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="File"
                    value={selectedOperation.file}
                    disabled
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Line"
                    type="number"
                    value={selectedOperation.line}
                    disabled
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      startIcon={<PreviewIcon />}
                      onClick={handlePreview}
                      disabled={isPreviewing}
                    >
                      Preview
                    </Button>
                    <Button
                      variant="contained"
                      onClick={handleApply}
                      disabled={selectedOperation.status === 'failed'}
                    >
                      Apply
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </>
        )}

        {selectedOperation?.status === 'failed' && (
          <Alert severity="error" sx={{ m: 2 }}>
            {selectedOperation.error}
          </Alert>
        )}

        {previewContent && (
          <>
            <Divider />
            <Box sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Preview</Typography>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: 'grey.100',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {previewContent}
              </Paper>
            </Box>
          </>
        )}

        {history.operations.length > 0 && (
          <>
            <Divider />
            <Box sx={{ p: 2 }}>
              <Typography variant="subtitle1" gutterBottom>History</Typography>
              <List>
                {history.operations.map((operation, index) => (
                  <ListItem
                    key={operation.id}
                    selected={index === history.currentIndex}
                    secondaryAction={
                      <Chip
                        label={operation.status}
                        color={
                          operation.status === 'applied' ? 'success' :
                          operation.status === 'failed' ? 'error' :
                          'default'
                        }
                      />
                    }
                  >
                    <ListItemIcon>
                      {REFACTORING_TYPES.find(t => t.id === operation.type)?.icon && (
                        <Box component={REFACTORING_TYPES.find(t => t.id === operation.type)?.icon} />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={REFACTORING_TYPES.find(t => t.id === operation.type)?.name}
                      secondary={`${operation.file}:${operation.line}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          </>
        )}
      </Box>

      <Dialog
        open={Boolean(selectedOperation)}
        onClose={() => setSelectedOperation(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {REFACTORING_TYPES.find(t => t.id === selectedOperation?.type)?.icon && (
              <Box component={REFACTORING_TYPES.find(t => t.id === selectedOperation?.type)?.icon} />
            )}
            {REFACTORING_TYPES.find(t => t.id === selectedOperation?.type)?.name}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Description</Typography>
            <Typography paragraph>{selectedOperation?.description}</Typography>

            <Typography variant="subtitle1" gutterBottom>Location</Typography>
            <Typography paragraph>{selectedOperation?.file}:{selectedOperation?.line}</Typography>

            {selectedOperation?.status === 'failed' && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {selectedOperation.error}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedOperation(null)}>Close</Button>
          {selectedOperation && selectedOperation.status !== 'failed' && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleApply}
            >
              Apply
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default RefactoringPanel; 