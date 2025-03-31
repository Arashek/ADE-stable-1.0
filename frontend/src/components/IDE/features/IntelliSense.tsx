import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material';
import {
  Code as CodeIcon,
  Functions as FunctionIcon,
  Class as ClassIcon,
  ViewModule as ModuleIcon,
  Extension as ExtensionIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { useCodebaseAwareness } from '../../../hooks/useCodebaseAwareness';

interface Suggestion {
  label: string;
  type: 'function' | 'class' | 'variable' | 'module' | 'property';
  description?: string;
  insertText: string;
  documentation?: string;
}

interface IntelliSenseProps {
  code: string;
  position: { line: number; column: number };
  language: string;
  onSuggestionSelect: (suggestion: Suggestion) => void;
}

export const IntelliSense: React.FC<IntelliSenseProps> = ({
  code,
  position,
  language,
  onSuggestionSelect,
}) => {
  const theme = useTheme();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { analyzeCode, getSymbols } = useCodebaseAwareness();

  useEffect(() => {
    const getSuggestions = async () => {
      try {
        const analysis = await analyzeCode(code, language);
        const symbols = await getSymbols(position.line, position.column);
        
        const newSuggestions = [...analysis.suggestions, ...symbols]
          .map(item => ({
            label: item.name,
            type: item.type,
            description: item.description,
            insertText: item.insertText || item.name,
            documentation: item.documentation
          }));

        setSuggestions(newSuggestions);
      } catch (error) {
        console.error('Failed to get suggestions:', error);
      }
    };

    getSuggestions();
  }, [code, position, language]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'function':
        return <FunctionIcon />;
      case 'class':
        return <ClassIcon />;
      case 'module':
        return <ModuleIcon />;
      default:
        return <CodeIcon />;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
        e.preventDefault();
        if (suggestions[selectedIndex]) {
          onSuggestionSelect(suggestions[selectedIndex]);
        }
        break;
    }
  };

  if (suggestions.length === 0) return null;

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        left: position.column * 8, // Approximate char width
        top: (position.line + 1) * 20, // Approximate line height
        maxWidth: 400,
        maxHeight: 300,
        overflow: 'auto',
        zIndex: 1000,
        backgroundColor: theme.palette.background.paper,
      }}
      onKeyDown={handleKeyDown}
    >
      <List dense>
        {suggestions.map((suggestion, index) => (
          <ListItem
            key={suggestion.label}
            button
            selected={index === selectedIndex}
            onClick={() => onSuggestionSelect(suggestion)}
            sx={{
              '&.Mui-selected': {
                backgroundColor: theme.palette.action.selected,
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>
              {getIcon(suggestion.type)}
            </ListItemIcon>
            <ListItemText
              primary={suggestion.label}
              secondary={
                suggestion.description && (
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    noWrap
                  >
                    {suggestion.description}
                  </Typography>
                )
              }
            />
            <Typography
              variant="caption"
              color="textSecondary"
              sx={{ ml: 1 }}
            >
              {suggestion.type}
            </Typography>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};
