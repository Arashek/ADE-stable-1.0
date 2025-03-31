import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  TextField,
  Chip,
  List,
  ListItem,
  ListItemText,
  Tooltip,
  Collapse,
  Divider,
} from '@mui/material';
import {
  Help as HelpIcon,
  Search as SearchIcon,
  Mic as MicIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Web as WebIcon,
  Code as CodeIcon,
  AutoAwesome as AgentVisualizationIcon,
  BugReport as DebugIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';

interface DocumentationItem {
  id: string;
  title: string;
  category: string;
  content: string;
  examples?: string[];
  relatedItems?: string[];
  tags: string[];
  icon: React.ReactNode;
}

const documentationItems: DocumentationItem[] = [
  {
    id: 'browser-overview',
    title: 'Custom Browser Overview',
    category: 'Browser',
    content: `The Custom Browser component provides a fully-featured web browser interface with the following capabilities:
    - URL navigation and history management
    - Bookmarks system
    - Developer tools
    - Responsive preview modes
    - Device frame simulation
    - Customizable preview settings`,
    examples: [
      'To navigate to a URL, enter it in the address bar and press Enter or click Go',
      'To add a bookmark, click the bookmark icon and fill in the details',
      'To toggle developer tools, click the DevTools icon in the toolbar'
    ],
    tags: ['browser', 'navigation', 'preview', 'devtools'],
    icon: <WebIcon />
  },
  {
    id: 'code-preview',
    title: 'Code Preview Features',
    category: 'Code',
    content: `The Code Preview component offers advanced code viewing capabilities:
    - Syntax highlighting for multiple languages
    - Line numbers
    - Copy to clipboard
    - Code sharing
    - Theme customization
    - Font size adjustment`,
    examples: [
      'To copy code, click the copy icon in the toolbar',
      'To change the theme, select from the theme dropdown',
      'To adjust font size, use the font size selector'
    ],
    tags: ['code', 'preview', 'syntax', 'sharing'],
    icon: <CodeIcon />
  },
  {
    id: 'agent-visualization',
    title: 'Agent Visualization Guide',
    category: 'Agents',
    content: `The Agent Visualization component provides multiple views of agent activities:
    - Grid view for quick overview
    - Network view for communication patterns
    - Timeline view for activity history
    - Metrics view for performance data
    - Heatmap view for activity patterns
    - Dependency view for agent relationships`,
    examples: [
      'Switch between visualization modes using the toolbar icons',
      'Filter agents by status using the status filter',
      'Search for specific agents using the search bar'
    ],
    tags: ['agents', 'visualization', 'metrics', 'network'],
    icon: <AgentVisualizationIcon />
  },
  {
    id: 'debugging-tools',
    title: 'Debugging Tools',
    category: 'Development',
    content: `The Development Environment includes comprehensive debugging tools:
    - Network request monitoring
    - Console logging
    - Performance metrics
    - Breakpoint management
    - Watch expressions
    - Source map support
    - Profiling capabilities
    - Code coverage tracking`,
    examples: [
      'Add breakpoints by clicking the line numbers',
      'Monitor network requests in the Network tab',
      'View performance metrics in real-time'
    ],
    tags: ['debugging', 'development', 'monitoring', 'performance'],
    icon: <DebugIcon />
  },
  {
    id: 'security-monitoring',
    title: 'Security Monitoring',
    category: 'Security',
    content: `Security features and monitoring capabilities:
    - Real-time security issue detection
    - Vulnerability scanning
    - Security best practices recommendations
    - Compliance checking
    - Access control monitoring`,
    examples: [
      'View security issues in the Security tab',
      'Check compliance status in the dashboard',
      'Review access logs in the monitoring section'
    ],
    tags: ['security', 'monitoring', 'compliance', 'vulnerability'],
    icon: <SecurityIcon />
  },
  {
    id: 'performance-monitoring',
    title: 'Performance Monitoring',
    category: 'Performance',
    content: `Comprehensive performance monitoring tools:
    - Real-time metrics tracking
    - Resource usage monitoring
    - Response time analysis
    - Error rate tracking
    - Performance optimization suggestions`,
    examples: [
      'Monitor FPS in the Performance tab',
      'Track memory usage in real-time',
      'Analyze network performance metrics'
    ],
    tags: ['performance', 'monitoring', 'metrics', 'optimization'],
    icon: <PerformanceIcon />
  }
];

export const DocumentationPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [isListening, setIsListening] = useState(false);

  const filteredItems = documentationItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = !selectedCategory || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(documentationItems.map(item => item.category)));

  const handleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
      };
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setSearchQuery(transcript);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognition.start();
    }
  };

  const toggleItem = (id: string) => {
    setExpandedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  return (
    <Paper
      sx={{
        position: 'fixed',
        top: 0,
        right: 0,
        height: '100vh',
        width: isOpen ? '400px' : '48px',
        transition: 'width 0.3s ease-in-out',
        zIndex: 1000,
        bgcolor: 'grey.900',
        color: 'white',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ p: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <IconButton onClick={() => setIsOpen(!isOpen)} color="inherit">
          {isOpen ? <ExpandMoreIcon /> : <ExpandLessIcon />}
        </IconButton>
        <Tooltip title="Documentation">
          <IconButton color="inherit">
            <HelpIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {isOpen && (
        <>
          <Box sx={{ p: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search documentation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                endAdornment: (
                  <IconButton size="small" onClick={handleVoiceInput}>
                    <MicIcon color={isListening ? 'primary' : 'inherit'} />
                  </IconButton>
                ),
              }}
            />
          </Box>

          <Box sx={{ p: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {categories.map(category => (
              <Chip
                key={category}
                label={category}
                onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
                color={selectedCategory === category ? 'primary' : 'default'}
                variant={selectedCategory === category ? 'filled' : 'outlined'}
              />
            ))}
          </Box>

          <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
            {filteredItems.map(item => (
              <Paper
                key={item.id}
                sx={{
                  mb: 2,
                  p: 2,
                  bgcolor: 'grey.800',
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'grey.700' },
                }}
                onClick={() => toggleItem(item.id)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {item.icon}
                  <Typography variant="subtitle1" sx={{ ml: 1 }}>
                    {item.title}
                  </Typography>
                </Box>
                {expandedItems.includes(item.id) && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" paragraph>
                      {item.content}
                    </Typography>
                    {item.examples && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Examples:
                        </Typography>
                        <List>
                          {item.examples.map((example, index) => (
                            <ListItem key={index}>
                              <ListItemText primary={example} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                    <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {item.tags.map(tag => (
                        <Chip key={tag} label={tag} size="small" />
                      ))}
                    </Box>
                  </Box>
                )}
              </Paper>
            ))}
          </Box>
        </>
      )}
    </Paper>
  );
}; 