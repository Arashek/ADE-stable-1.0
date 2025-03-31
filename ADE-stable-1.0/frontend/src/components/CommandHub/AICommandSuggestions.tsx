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
  Fade,
  styled,
} from '@mui/material';
import {
  Lightbulb as SuggestionIcon,
  KeyboardArrowRight as ArrowIcon,
} from '@mui/icons-material';

const SuggestionsContainer = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: '100%',
  left: 0,
  right: 0,
  marginTop: theme.spacing(1),
  zIndex: theme.zIndex.modal,
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[4],
  borderRadius: theme.shape.borderRadius,
  overflow: 'hidden',
}));

const StyledList = styled(List)({
  padding: 0,
});

const StyledListItem = styled(ListItem)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  cursor: 'pointer',
  transition: 'background-color 0.2s ease-in-out',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const StyledListItemText = styled(ListItemText)({
  margin: 0,
});

const StyledListItemIcon = styled(ListItemIcon)(({ theme }) => ({
  minWidth: 40,
  color: theme.palette.primary.main,
}));

const StyledArrowIcon = styled(IconButton)(({ theme }) => ({
  color: theme.palette.text.secondary,
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateX(4px)',
  },
}));

const TitleContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  display: 'flex',
  alignItems: 'center',
}));

const TitleIcon = styled(SuggestionIcon)(({ theme }) => ({
  marginRight: theme.spacing(1),
}));

interface CommandSuggestion {
  id: string;
  command: string;
  description: string;
  category: string;
}

interface AICommandSuggestionsProps {
  query: string;
  onSelect: (suggestion: CommandSuggestion) => void;
  visible: boolean;
}

export const AICommandSuggestions: React.FC<AICommandSuggestionsProps> = ({
  query,
  onSelect,
  visible,
}) => {
  const [suggestions, setSuggestions] = useState<CommandSuggestion[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!query.trim()) {
        setSuggestions([]);
        return;
      }

      setLoading(true);
      try {
        const response = await fetch('/api/command-suggestions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch suggestions');
        }

        const data = await response.json();
        setSuggestions(data.suggestions);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimeout = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounceTimeout);
  }, [query]);

  if (!visible || suggestions.length === 0) {
    return null;
  }

  return (
    <Fade in={visible}>
      <SuggestionsContainer>
        <StyledPaper>
          <TitleContainer>
            <TitleIcon />
            <Typography variant="subtitle2">AI Suggestions</Typography>
          </TitleContainer>
          <StyledList>
            {suggestions.map((suggestion) => (
              <StyledListItem
                key={suggestion.id}
                onClick={() => onSelect(suggestion)}
              >
                <StyledListItemIcon>
                  <SuggestionIcon />
                </StyledListItemIcon>
                <StyledListItemText
                  primary={suggestion.command}
                  secondary={suggestion.description}
                />
                <StyledArrowIcon size="small">
                  <ArrowIcon />
                </StyledArrowIcon>
              </StyledListItem>
            ))}
          </StyledList>
        </StyledPaper>
      </SuggestionsContainer>
    </Fade>
  );
}; 