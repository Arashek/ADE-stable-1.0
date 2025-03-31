import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  ExpandMore,
  Code,
  Settings,
  Edit,
  Add,
  Delete,
  Folder,
  Description,
  PlayArrow,
  Build,
  BugReport,
} from '@mui/icons-material';
import { JsonEditor as Editor } from 'jsoneditor-react';
import 'jsoneditor-react/es/editor.min.css';

const ConfigContainer = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
}));

const ScrollableContent = styled(Box)({
  flex: 1,
  overflow: 'auto',
  padding: '16px',
});

interface BoundariesConfigProps {
  onConfigChange: (config: any) => void;
}

const BoundariesConfig: React.FC<BoundariesConfigProps> = ({ onConfigChange }) => {
  const [config, setConfig] = useState<any>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedConfig, setEditedConfig] = useState<any>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await fetch('/.boundaries/commands.json');
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Failed to load Boundaries configuration:', error);
    }
  };

  const handleSave = async () => {
    try {
      const response = await fetch('/.boundaries/commands.json', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editedConfig),
      });

      if (response.ok) {
        setConfig(editedConfig);
        onConfigChange(editedConfig);
      }
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
    setIsEditing(false);
  };

  const renderCommandIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'preview':
        return <PlayArrow />;
      case 'build':
        return <Build />;
      case 'test':
        return <BugReport />;
      default:
        return <Code />;
    }
  };

  const renderFrameworkCommands = (framework: string, commands: any) => (
    <Accordion key={framework}>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Folder />
          <Typography>{framework}</Typography>
          <Chip
            label={Object.keys(commands).length}
            size="small"
            sx={{ ml: 1 }}
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <List dense>
          {Object.entries(commands).map(([id, cmd]: [string, any]) => (
            <ListItem
              key={id}
              secondaryAction={
                <Tooltip title="Edit Command">
                  <IconButton edge="end" size="small">
                    <Edit fontSize="small" />
                  </IconButton>
                </Tooltip>
              }
            >
              <ListItemIcon>
                {renderCommandIcon(cmd.category || 'default')}
              </ListItemIcon>
              <ListItemText
                primary={cmd.name || id}
                secondary={cmd.description}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
          ))}
        </List>
      </AccordionDetails>
    </Accordion>
  );

  const renderConfigSection = (section: string, data: any) => (
    <Accordion
      key={section}
      expanded={selectedSection === section}
      onChange={() => setSelectedSection(selectedSection === section ? null : section)}
    >
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Description />
          <Typography>{section}</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        {section === 'commands' ? (
          Object.entries(data).map(([framework, commands]: [string, any]) =>
            renderFrameworkCommands(framework, commands)
          )
        ) : (
          <pre style={{ margin: 0, fontSize: '0.875rem' }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </AccordionDetails>
    </Accordion>
  );

  return (
    <ConfigContainer>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Boundaries Configuration</Typography>
          <Box>
            <Tooltip title="Edit Configuration">
              <IconButton size="small" onClick={() => setIsEditing(true)}>
                <Edit />
              </IconButton>
            </Tooltip>
            <Tooltip title="Add Command">
              <IconButton size="small">
                <Add />
              </IconButton>
            </Tooltip>
            <Tooltip title="Settings">
              <IconButton size="small">
                <Settings />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>

      <ScrollableContent>
        {config && Object.entries(config).map(([section, data]) =>
          renderConfigSection(section, data)
        )}
      </ScrollableContent>

      <Dialog
        open={isEditing}
        onClose={() => setIsEditing(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Configuration</DialogTitle>
        <DialogContent>
          <Box sx={{ height: '60vh' }}>
            <Editor
              value={editedConfig || config}
              onChange={setEditedConfig}
              mode="tree"
              navigationBar={false}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditing(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </ConfigContainer>
  );
};

export default BoundariesConfig; 