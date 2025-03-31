import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  History as HistoryIcon,
  Compare as CompareIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
} from '@mui/icons-material';

interface CodeChange {
  id: string;
  timestamp: string;
  description: string;
  filename: string;
  diff: string;
  author: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`code-tabpanel-${index}`}
    aria-labelledby={`code-tab-${index}`}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const CodeEvolution: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [changes] = useState<CodeChange[]>([
    {
      id: '1',
      timestamp: '10:30 AM',
      description: 'Updated authentication logic',
      filename: 'auth.ts',
      diff: `@@ -1,7 +1,7 @@
- function authenticate(user) {
+ async function authenticate(user: User) {
-   const token = generateToken();
+   const token = await generateToken(user);
    return token;
  }`,
      author: 'AI Assistant',
    },
    {
      id: '2',
      timestamp: '10:35 AM',
      description: 'Added error handling',
      filename: 'auth.ts',
      diff: `@@ -1,5 +1,9 @@
  async function authenticate(user: User) {
+   try {
    const token = await generateToken(user);
    return token;
+   } catch (error) {
+     throw new AuthError('Failed to authenticate user');
+   }
  }`,
      author: 'AI Assistant',
    },
  ]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="Changes" />
          <Tab label="Diff View" />
        </Tabs>
      </Box>

      <TabPanel value={currentTab} index={0}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {changes.map((change) => (
            <Paper key={change.id} sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="subtitle1">{change.description}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {change.timestamp}
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {change.filename}
              </Typography>
              <Box
                component="pre"
                sx={{
                  backgroundColor: 'grey.900',
                  color: 'common.white',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: '0.875rem',
                  fontFamily: 'monospace',
                }}
              >
                {change.diff}
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  By {change.author}
                </Typography>
              </Box>
            </Paper>
          ))}
        </Box>
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <Box sx={{ display: 'flex', gap: 2, height: '100%' }}>
          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Previous Version
            </Typography>
            <Box
              component="pre"
              sx={{
                backgroundColor: 'grey.900',
                color: 'common.white',
                p: 2,
                borderRadius: 1,
                overflow: 'auto',
                height: 'calc(100% - 40px)',
                fontSize: '0.875rem',
                fontFamily: 'monospace',
              }}
            >
              {changes[currentTab]?.diff.split('\n').map((line) => (
                <div key={line}>
                  {line.startsWith('-') ? (
                    <span style={{ color: '#ff8080' }}>{line}</span>
                  ) : (
                    line
                  )}
                </div>
              ))}
            </Box>
          </Paper>

          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Current Version
            </Typography>
            <Box
              component="pre"
              sx={{
                backgroundColor: 'grey.900',
                color: 'common.white',
                p: 2,
                borderRadius: 1,
                overflow: 'auto',
                height: 'calc(100% - 40px)',
                fontSize: '0.875rem',
                fontFamily: 'monospace',
              }}
            >
              {changes[currentTab]?.diff.split('\n').map((line) => (
                <div key={line}>
                  {line.startsWith('+') ? (
                    <span style={{ color: '#80ff80' }}>{line}</span>
                  ) : (
                    line
                  )}
                </div>
              ))}
            </Box>
          </Paper>
        </Box>
      </TabPanel>

      <Box
        sx={{
          mt: 'auto',
          pt: 2,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <Box>
          <Tooltip title="View History">
            <IconButton>
              <HistoryIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Compare Versions">
            <IconButton>
              <CompareIcon />
            </IconButton>
          </Tooltip>
        </Box>
        <Box>
          <Tooltip title="Undo">
            <IconButton>
              <UndoIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Redo">
            <IconButton>
              <RedoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
    </Box>
  );
};

export default CodeEvolution; 