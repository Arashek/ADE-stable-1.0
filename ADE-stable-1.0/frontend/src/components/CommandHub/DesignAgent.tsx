import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  IconButton,
  Tooltip,
  Drawer,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  makeStyles,
  Theme,
  createStyles,
} from '@material-ui/core';
import {
  Palette as PaletteIcon,
  ViewQuilt as LayoutIcon,
  Style as StyleIcon,
  Preview as PreviewIcon,
  Save as SaveIcon,
  Code as CodeIcon,
  Chat as ChatIcon,
  Close as CloseIcon,
  Add as AddIcon,
  Edit as EditIcon,
} from '@material-ui/icons';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    },
    header: {
      padding: theme.spacing(2),
      borderBottom: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    content: {
      flex: 1,
      display: 'flex',
      overflow: 'hidden',
    },
    sidebar: {
      width: 300,
      borderRight: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      flexDirection: 'column',
    },
    canvas: {
      flex: 1,
      padding: theme.spacing(2),
      backgroundColor: theme.palette.background.default,
      position: 'relative',
    },
    previewContainer: {
      border: `1px solid ${theme.palette.divider}`,
      borderRadius: theme.shape.borderRadius,
      height: '100%',
      overflow: 'auto',
      backgroundColor: '#fff',
    },
    toolbar: {
      padding: theme.spacing(1),
      borderBottom: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      gap: theme.spacing(1),
    },
    chatDrawer: {
      width: 320,
      padding: theme.spacing(2),
    },
    chatInput: {
      position: 'absolute',
      bottom: 0,
      left: 0,
      right: 0,
      padding: theme.spacing(2),
      backgroundColor: theme.palette.background.paper,
      borderTop: `1px solid ${theme.palette.divider}`,
    },
    chatMessages: {
      height: 'calc(100% - 80px)',
      overflowY: 'auto',
      padding: theme.spacing(2),
    },
    message: {
      marginBottom: theme.spacing(2),
      padding: theme.spacing(1),
      borderRadius: theme.shape.borderRadius,
      maxWidth: '80%',
    },
    userMessage: {
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.primary.contrastText,
      marginLeft: 'auto',
    },
    agentMessage: {
      backgroundColor: theme.palette.grey[100],
    },
    fab: {
      position: 'absolute',
      bottom: theme.spacing(2),
      right: theme.spacing(2),
    },
    componentList: {
      padding: theme.spacing(2),
    },
    componentItem: {
      marginBottom: theme.spacing(1),
      padding: theme.spacing(1),
      border: `1px solid ${theme.palette.divider}`,
      borderRadius: theme.shape.borderRadius,
      cursor: 'pointer',
      '&:hover': {
        backgroundColor: theme.palette.action.hover,
      },
    },
  })
);

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
}

interface DesignAgentProps {
  projectId: string;
  onSave: (design: any) => void;
  onGenerateCode: (design: any) => void;
}

const DesignAgent: React.FC<DesignAgentProps> = ({ projectId, onSave, onGenerateCode }) => {
  const classes = useStyles();
  const [activeTab, setActiveTab] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [showComponentDialog, setShowComponentDialog] = useState(false);
  const [currentDesign, setCurrentDesign] = useState<any>({
    layout: {},
    styles: {},
    components: [],
  });
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const handleTabChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSave = () => {
    onSave(currentDesign);
  };

  const handleGenerateCode = () => {
    onGenerateCode(currentDesign);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');

    // Simulate agent response
    setTimeout(() => {
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'I understand you want to modify the design. Let me help you with that.',
        sender: 'agent',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, agentMessage]);
      scrollToBottom();
    }, 1000);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const toggleChat = () => {
    setChatOpen(!chatOpen);
  };

  return (
    <div className={classes.root}>
      <div className={classes.header}>
        <Typography variant="h6">Design Agent</Typography>
        <Box>
          <Tooltip title="Save Design">
            <IconButton onClick={handleSave}>
              <SaveIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Generate Code">
            <IconButton onClick={handleGenerateCode}>
              <CodeIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Toggle Chat">
            <IconButton onClick={toggleChat}>
              <ChatIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </div>
      
      <div className={classes.content}>
        <Paper className={classes.sidebar}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<LayoutIcon />} label="Layout" />
            <Tab icon={<StyleIcon />} label="Style" />
            <Tab icon={<PaletteIcon />} label="Theme" />
          </Tabs>
          
          <div className={classes.toolbar}>
            <Tooltip title="Add Component">
              <IconButton size="small" onClick={() => setShowComponentDialog(true)}>
                <AddIcon />
              </IconButton>
            </Tooltip>
          </div>
          
          <div className={classes.componentList}>
            {currentDesign.components.map((component: any, index: number) => (
              <div key={index} className={classes.componentItem}>
                <Typography variant="subtitle2">{component.name}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {component.type}
                </Typography>
              </div>
            ))}
          </div>
        </Paper>
        
        <div className={classes.canvas}>
          <Box className={classes.previewContainer}>
            {/* Live preview of the design */}
            <Typography variant="body2" color="textSecondary" align="center">
              Design Preview
            </Typography>
          </Box>
          
          <Fab
            color="primary"
            className={classes.fab}
            onClick={() => setShowComponentDialog(true)}
          >
            <AddIcon />
          </Fab>
        </div>
      </div>

      {/* Chat Drawer */}
      <Drawer
        anchor="right"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        classes={{ paper: classes.chatDrawer }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Design Assistant</Typography>
          <IconButton onClick={() => setChatOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>

        <div className={classes.chatMessages}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`${classes.message} ${
                message.sender === 'user' ? classes.userMessage : classes.agentMessage
              }`}
            >
              <Typography variant="body2">{message.text}</Typography>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className={classes.chatInput}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask the design agent..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            size="small"
          />
        </div>
      </Drawer>

      {/* Add Component Dialog */}
      <Dialog
        open={showComponentDialog}
        onClose={() => setShowComponentDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Component</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Component Name"
            fullWidth
            variant="outlined"
          />
          {/* Add more component configuration options */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowComponentDialog(false)}>Cancel</Button>
          <Button color="primary" onClick={() => setShowComponentDialog(false)}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default DesignAgent; 