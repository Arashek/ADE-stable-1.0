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
} from '@mui/material';
import { styled } from '@mui/material/styles';
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
} from '@mui/icons-material';

const StyledRoot = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const StyledHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const StyledContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}));

const StyledSidebar = styled(Box)(({ theme }) => ({
  width: 300,
  borderRight: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  flexDirection: 'column',
}));

const StyledCanvas = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.default,
  position: 'relative',
}));

const StyledPreviewContainer = styled(Box)(({ theme }) => ({
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  height: '100%',
  overflow: 'auto',
  backgroundColor: '#fff',
}));

const StyledToolbar = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  gap: theme.spacing(1),
}));

const StyledChatDrawer = styled(Box)(({ theme }) => ({
  width: 320,
  padding: theme.spacing(2),
}));

const StyledChatInput = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: 0,
  left: 0,
  right: 0,
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderTop: `1px solid ${theme.palette.divider}`,
}));

const StyledChatMessages = styled(Box)(({ theme }) => ({
  height: 'calc(100% - 80px)',
  overflowY: 'auto',
  padding: theme.spacing(2),
}));

const StyledMessage = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  padding: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  maxWidth: '80%',
}));

const StyledUserMessage = styled(StyledMessage)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  marginLeft: 'auto',
}));

const StyledAgentMessage = styled(StyledMessage)(({ theme }) => ({
  backgroundColor: theme.palette.grey[100],
}));

const StyledFab = styled(Fab)(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
}));

const StyledComponentList = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
}));

const StyledComponentItem = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(1),
  padding: theme.spacing(1),
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

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
    <StyledRoot>
      <StyledHeader>
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
      </StyledHeader>
      
      <StyledContent>
        <StyledSidebar>
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
          
          <StyledToolbar>
            <Tooltip title="Add Component">
              <IconButton size="small" onClick={() => setShowComponentDialog(true)}>
                <AddIcon />
              </IconButton>
            </Tooltip>
          </StyledToolbar>
          
          <StyledComponentList>
            {currentDesign.components.map((component: any, index: number) => (
              <StyledComponentItem key={index}>
                <Typography variant="subtitle2">{component.name}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {component.type}
                </Typography>
              </StyledComponentItem>
            ))}
          </StyledComponentList>
        </StyledSidebar>
        
        <StyledCanvas>
          <StyledPreviewContainer>
            {/* Live preview of the design */}
            <Typography variant="body2" color="textSecondary" align="center">
              Design Preview
            </Typography>
          </StyledPreviewContainer>
          
          <StyledFab
            color="primary"
            onClick={() => setShowComponentDialog(true)}
          >
            <AddIcon />
          </StyledFab>
        </StyledCanvas>
      </StyledContent>

      {/* Chat Drawer */}
      <Drawer
        anchor="right"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        sx={{ 
          '& .MuiDrawer-paper': {
            width: 320,
            padding: 2
          }
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Design Assistant</Typography>
          <IconButton onClick={() => setChatOpen(false)}>
            <CloseIcon />
          </IconButton>
        </Box>

        <StyledChatMessages>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                marginBottom: 2,
                padding: 1,
                borderRadius: 1,
                maxWidth: '80%',
                ...(message.sender === 'user' 
                  ? {
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                      marginLeft: 'auto'
                    } 
                  : {
                      backgroundColor: 'grey.100'
                    }
                )
              }}
            >
              <Typography variant="body2">{message.text}</Typography>
            </Box>
          ))}
          <div ref={chatEndRef} />
        </StyledChatMessages>

        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: 2,
            backgroundColor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider'
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask the design agent..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            size="small"
          />
        </Box>
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
    </StyledRoot>
  );
};

export default DesignAgent;