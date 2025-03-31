import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Avatar,
  Divider,
  Chip,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  Add as AddIcon,
  AttachFile as AttachFileIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as UncheckedIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  Description as DescriptionIcon,
  Link as LinkIcon,
} from '@mui/icons-material';

interface Message {
  id: string;
  sender: {
    id: string;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  attachments?: Array<{
    name: string;
    type: string;
    url: string;
  }>;
}

interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string[];
  dueDate: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  createdBy: string;
  createdAt: string;
}

interface Resource {
  id: string;
  title: string;
  type: 'document' | 'link' | 'file';
  url: string;
  description: string;
  uploadedBy: string;
  uploadedAt: string;
  tags: string[];
}

const TeamCollaboration: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: {
        id: '1',
        name: 'John Doe',
        avatar: 'https://via.placeholder.com/40',
      },
      content: 'Hey team! How is everyone doing?',
      timestamp: '2024-01-01T10:00:00Z',
    },
  ]);
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Implement user authentication',
      description: 'Add JWT-based authentication system',
      assignedTo: ['1', '2'],
      dueDate: '2024-01-15',
      status: 'in_progress',
      priority: 'high',
      createdBy: '1',
      createdAt: '2024-01-01T10:00:00Z',
    },
  ]);
  const [resources, setResources] = useState<Resource[]>([
    {
      id: '1',
      title: 'Project Documentation',
      type: 'document',
      url: 'https://example.com/docs',
      description: 'Main project documentation',
      uploadedBy: '1',
      uploadedAt: '2024-01-01T10:00:00Z',
      tags: ['documentation', 'guide'],
    },
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    assignedTo: [] as string[],
    dueDate: '',
    priority: 'medium' as Task['priority'],
  });
  const [newResource, setNewResource] = useState({
    title: '',
    type: 'document' as Resource['type'],
    url: '',
    description: '',
    tags: [] as string[],
  });
  const [openTaskDialog, setOpenTaskDialog] = useState(false);
  const [openResourceDialog, setOpenResourceDialog] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    const message: Message = {
      id: Date.now().toString(),
      sender: {
        id: '1', // Current user ID
        name: 'John Doe', // Current user name
        avatar: 'https://via.placeholder.com/40',
      },
      content: newMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, message]);
    setNewMessage('');
  };

  const handleCreateTask = () => {
    const task: Task = {
      id: Date.now().toString(),
      ...newTask,
      status: 'todo',
      createdBy: '1', // Current user ID
      createdAt: new Date().toISOString(),
    };

    setTasks([...tasks, task]);
    setOpenTaskDialog(false);
    setNewTask({
      title: '',
      description: '',
      assignedTo: [],
      dueDate: '',
      priority: 'medium',
    });
  };

  const handleCreateResource = () => {
    const resource: Resource = {
      id: Date.now().toString(),
      ...newResource,
      uploadedBy: '1', // Current user ID
      uploadedAt: new Date().toISOString(),
    };

    setResources([...resources, resource]);
    setOpenResourceDialog(false);
    setNewResource({
      title: '',
      type: 'document',
      url: '',
      description: '',
      tags: [],
    });
  };

  const handleTaskStatusChange = (taskId: string, newStatus: Task['status']) => {
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, status: newStatus } : task
    ));
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Team Chat */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Team Chat
            </Typography>
            <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2 }}>
              {messages.map((message) => (
                <Box key={message.id} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                    <Avatar src={message.sender.avatar} sx={{ mr: 1 }}>
                      <PersonIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2">
                        {message.sender.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(message.timestamp).toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body1" sx={{ ml: 7 }}>
                    {message.content}
                  </Typography>
                  {message.attachments && message.attachments.length > 0 && (
                    <Box sx={{ ml: 7, mt: 1 }}>
                      {message.attachments.map((attachment) => (
                        <Chip
                          key={attachment.name}
                          icon={<AttachFileIcon />}
                          label={attachment.name}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              ))}
              <div ref={messagesEndRef} />
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                placeholder="Type a message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <IconButton color="primary" onClick={handleSendMessage}>
                <SendIcon />
              </IconButton>
            </Box>
          </Paper>
        </Grid>

        {/* Tasks and Resources */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Tasks" />
              <Tab label="Resources" />
            </Tabs>
            <Box sx={{ mt: 2 }}>
              {activeTab === 0 ? (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1">Tasks</Typography>
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => setOpenTaskDialog(true)}
                    >
                      Add Task
                    </Button>
                  </Box>
                  <List>
                    {tasks.map((task) => (
                      <ListItem key={task.id}>
                        <ListItemAvatar>
                          <IconButton
                            onClick={() => handleTaskStatusChange(
                              task.id,
                              task.status === 'done' ? 'todo' : 'done'
                            )}
                          >
                            {task.status === 'done' ? (
                              <CheckCircleIcon color="success" />
                            ) : (
                              <UncheckedIcon />
                            )}
                          </IconButton>
                        </ListItemAvatar>
                        <ListItemText
                          primary={task.title}
                          secondary={
                            <Box>
                              <Typography component="span" variant="body2">
                                {task.description}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                <Chip
                                  size="small"
                                  label={task.priority}
                                  color={getPriorityColor(task.priority)}
                                  sx={{ mr: 1 }}
                                />
                                <Chip
                                  size="small"
                                  label={task.status}
                                  sx={{ mr: 1 }}
                                />
                                <Chip
                                  size="small"
                                  label={`Due: ${new Date(task.dueDate).toLocaleDateString()}`}
                                />
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Tooltip title="Edit">
                            <IconButton edge="end" sx={{ mr: 1 }}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton edge="end">
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </>
              ) : (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1">Resources</Typography>
                    <Button
                      startIcon={<AddIcon />}
                      onClick={() => setOpenResourceDialog(true)}
                    >
                      Add Resource
                    </Button>
                  </Box>
                  <List>
                    {resources.map((resource) => (
                      <ListItem key={resource.id}>
                        <ListItemAvatar>
                          <Avatar>
                            {resource.type === 'document' ? (
                              <DescriptionIcon />
                            ) : resource.type === 'link' ? (
                              <LinkIcon />
                            ) : (
                              <AttachFileIcon />
                            )}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={resource.title}
                          secondary={
                            <Box>
                              <Typography component="span" variant="body2">
                                {resource.description}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                {resource.tags.map((tag) => (
                                  <Chip
                                    key={tag}
                                    size="small"
                                    label={tag}
                                    sx={{ mr: 1, mb: 1 }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Tooltip title="Edit">
                            <IconButton edge="end" sx={{ mr: 1 }}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton edge="end">
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Add Task Dialog */}
      <Dialog open={openTaskDialog} onClose={() => setOpenTaskDialog(false)}>
        <DialogTitle>Add New Task</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            value={newTask.title}
            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newTask.description}
            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Assigned To</InputLabel>
            <Select
              multiple
              value={newTask.assignedTo}
              label="Assigned To"
              onChange={(e) => setNewTask({ ...newTask, assignedTo: e.target.value as string[] })}
            >
              <MenuItem value="1">John Doe</MenuItem>
              <MenuItem value="2">Jane Smith</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Due Date"
            type="date"
            fullWidth
            value={newTask.dueDate}
            onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Priority</InputLabel>
            <Select
              value={newTask.priority}
              label="Priority"
              onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as Task['priority'] })}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTaskDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTask} variant="contained">
            Create Task
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Resource Dialog */}
      <Dialog open={openResourceDialog} onClose={() => setOpenResourceDialog(false)}>
        <DialogTitle>Add New Resource</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            value={newResource.title}
            onChange={(e) => setNewResource({ ...newResource, title: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Type</InputLabel>
            <Select
              value={newResource.type}
              label="Type"
              onChange={(e) => setNewResource({ ...newResource, type: e.target.value as Resource['type'] })}
            >
              <MenuItem value="document">Document</MenuItem>
              <MenuItem value="link">Link</MenuItem>
              <MenuItem value="file">File</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="URL"
            fullWidth
            value={newResource.url}
            onChange={(e) => setNewResource({ ...newResource, url: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newResource.description}
            onChange={(e) => setNewResource({ ...newResource, description: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Tags</InputLabel>
            <Select
              multiple
              value={newResource.tags}
              label="Tags"
              onChange={(e) => setNewResource({ ...newResource, tags: e.target.value as string[] })}
            >
              <MenuItem value="documentation">Documentation</MenuItem>
              <MenuItem value="guide">Guide</MenuItem>
              <MenuItem value="reference">Reference</MenuItem>
              <MenuItem value="tutorial">Tutorial</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenResourceDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateResource} variant="contained">
            Add Resource
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TeamCollaboration; 