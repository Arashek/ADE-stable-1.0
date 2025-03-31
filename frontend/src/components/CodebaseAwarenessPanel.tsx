import React from 'react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Code as CodeIcon,
  Functions as FunctionIcon,
  Class as ClassIcon,
  Category as InterfaceIcon,
  Storage as VariableIcon,
  DataObject as TypeIcon
} from '@mui/icons-material';

interface Symbol {
  name: string;
  type: string;
  location: {
    start: { line: number; column: number };
    end: { line: number; column: number };
  };
}

export interface CodebaseAwarenessPanelProps {
  currentFile: string;
  onSymbolClick: (symbol: Symbol) => void;
}

const getSymbolIcon = (type: string) => {
  switch (type) {
    case 'function':
      return <FunctionIcon />;
    case 'class':
      return <ClassIcon />;
    case 'interface':
      return <InterfaceIcon />;
    case 'variable':
      return <VariableIcon />;
    case 'type':
      return <TypeIcon />;
    default:
      return <CodeIcon />;
  }
};

export const CodebaseAwarenessPanel: React.FC<CodebaseAwarenessPanelProps> = ({
  currentFile,
  onSymbolClick
}) => {
  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Codebase Awareness
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {currentFile}
      </Typography>
      <List>
        {/* Symbols will be populated here */}
      </List>
    </Paper>
  );
}; 