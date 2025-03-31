import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Code as CodeIcon,
  Compare as CompareIcon,
  History as HistoryIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';

interface CodeChange {
  id: string;
  file: string;
  timestamp: Date;
  author: string;
  changes: {
    before: string;
    after: string;
  };
}

const CodeEvolution: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedChange, setSelectedChange] = useState<CodeChange | null>(null);

  // Mock data - replace with actual data from API
  const codeChanges: CodeChange[] = [
    {
      id: '1',
      file: 'src/components/CommandPanel.tsx',
      timestamp: new Date('2024-03-19T10:00:00'),
      author: 'System Agent',
      changes: {
        before: `// Old code
const CommandPanel = () => {
  return <div>Old Panel</div>;
};`,
        after: `// New code
const CommandPanel = () => {
  const [command, setCommand] = useState('');
  return <div>New Panel</div>;
};`,
      },
    },
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const editorOptions = {
    readOnly: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontSize: 14,
    lineNumbers: 'on',
    renderWhitespace: 'selection',
    theme: 'vs-dark',
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        mb: 2,
        backgroundColor: 'background.paper',
        height: '400px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <CodeIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Code Evolution</Typography>
        <Box sx={{ ml: 'auto' }}>
          <Tooltip title="Refresh Changes">
            <IconButton size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab
          icon={<CompareIcon />}
          label="Diff View"
          iconPosition="start"
        />
        <Tab
          icon={<HistoryIcon />}
          label="History"
          iconPosition="start"
        />
      </Tabs>

      <Box sx={{ flex: 1, display: 'flex', mt: 2 }}>
        {activeTab === 0 ? (
          // Diff View
          <Box sx={{ display: 'flex', flex: 1, gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Before
              </Typography>
              <Editor
                height="100%"
                defaultLanguage="typescript"
                defaultValue={selectedChange?.changes.before || ''}
                options={editorOptions}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary">
                After
              </Typography>
              <Editor
                height="100%"
                defaultLanguage="typescript"
                defaultValue={selectedChange?.changes.after || ''}
                options={editorOptions}
              />
            </Box>
          </Box>
        ) : (
          // History View
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            {codeChanges.map((change) => (
              <Box
                key={change.id}
                sx={{
                  p: 2,
                  borderBottom: 1,
                  borderColor: 'divider',
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
                onClick={() => setSelectedChange(change)}
              >
                <Typography variant="subtitle2">{change.file}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {change.timestamp.toLocaleString()} by {change.author}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default CodeEvolution; 