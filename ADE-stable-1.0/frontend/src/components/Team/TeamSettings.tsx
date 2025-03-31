import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
  Code as CodeIcon,
} from '@mui/icons-material';

interface TeamSetting {
  id: string;
  name: string;
  description: string;
  value: string | boolean | string[];
  type: 'text' | 'boolean' | 'select' | 'multiselect';
  options?: string[];
}

const defaultSettings: TeamSetting[] = [
  {
    id: 'notifications',
    name: 'Team Notifications',
    description: 'Configure notification preferences for the team',
    value: true,
    type: 'boolean',
  },
  {
    id: 'code_review',
    name: 'Code Review Settings',
    description: 'Settings for code review process',
    value: ['pull_request', 'comments', 'approval'],
    type: 'multiselect',
    options: ['pull_request', 'comments', 'approval', 'automated_tests'],
  },
  {
    id: 'working_hours',
    name: 'Working Hours',
    description: 'Team working hours and timezone',
    value: 'UTC',
    type: 'select',
    options: ['UTC', 'EST', 'PST', 'GMT'],
  },
  {
    id: 'branch_naming',
    name: 'Branch Naming Convention',
    description: 'Pattern for branch naming',
    value: 'feature/{ticket}-{description}',
    type: 'text',
  },
];

const TeamSettings: React.FC = () => {
  const [settings, setSettings] = useState<TeamSetting[]>(defaultSettings);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingSetting, setEditingSetting] = useState<TeamSetting | null>(null);
  const [newSetting, setNewSetting] = useState<Partial<TeamSetting>>({
    name: '',
    description: '',
    type: 'text',
    value: '',
  });
  const [showSuccess, setShowSuccess] = useState(false);

  const handleOpenDialog = (setting?: TeamSetting) => {
    if (setting) {
      setEditingSetting(setting);
      setNewSetting(setting);
    } else {
      setEditingSetting(null);
      setNewSetting({
        name: '',
        description: '',
        type: 'text',
        value: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingSetting(null);
    setNewSetting({
      name: '',
      description: '',
      type: 'text',
      value: '',
    });
  };

  const handleSaveSetting = () => {
    if (editingSetting) {
      setSettings(settings.map(setting =>
        setting.id === editingSetting.id
          ? { ...setting, ...newSetting }
          : setting
      ));
    } else {
      setSettings([
        ...settings,
        {
          id: Date.now().toString(),
          ...newSetting as TeamSetting,
        },
      ]);
    }
    handleCloseDialog();
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleDeleteSetting = (id: string) => {
    setSettings(settings.filter(setting => setting.id !== id));
  };

  const handleValueChange = (value: any) => {
    setNewSetting({ ...newSetting, value });
  };

  const renderSettingValue = (setting: TeamSetting) => {
    switch (setting.type) {
      case 'boolean':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={setting.value as boolean}
                onChange={(e) => handleValueChange(e.target.checked)}
              />
            }
            label=""
          />
        );
      case 'select':
        return (
          <FormControl fullWidth>
            <InputLabel>Value</InputLabel>
            <Select
              value={setting.value as string}
              label="Value"
              onChange={(e) => handleValueChange(e.target.value)}
            >
              {setting.options?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      case 'multiselect':
        return (
          <FormControl fullWidth>
            <InputLabel>Values</InputLabel>
            <Select
              multiple
              value={setting.value as string[]}
              label="Values"
              onChange={(e) => handleValueChange(e.target.value)}
            >
              {setting.options?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      default:
        return (
          <TextField
            fullWidth
            value={setting.value as string}
            onChange={(e) => handleValueChange(e.target.value)}
          />
        );
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {showSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                <GroupIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                General Settings
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog()}
              >
                Add Setting
              </Button>
            </Box>
            <List>
              {settings.map((setting) => (
                <React.Fragment key={setting.id}>
                  <ListItem>
                    <ListItemText
                      primary={setting.name}
                      secondary={setting.description}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleOpenDialog(setting)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        edge="end"
                        onClick={() => handleDeleteSetting(setting.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<NotificationsIcon />}
                >
                  Configure Notifications
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<SecurityIcon />}
                >
                  Security Settings
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<ScheduleIcon />}
                >
                  Schedule Settings
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<CodeIcon />}
                >
                  Code Review Rules
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Add/Edit Setting Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingSetting ? 'Edit Setting' : 'Add New Setting'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newSetting.name}
            onChange={(e) => setNewSetting({ ...newSetting, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newSetting.description}
            onChange={(e) => setNewSetting({ ...newSetting, description: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Type</InputLabel>
            <Select
              value={newSetting.type}
              label="Type"
              onChange={(e) => setNewSetting({ ...newSetting, type: e.target.value as TeamSetting['type'] })}
            >
              <MenuItem value="text">Text</MenuItem>
              <MenuItem value="boolean">Boolean</MenuItem>
              <MenuItem value="select">Select</MenuItem>
              <MenuItem value="multiselect">Multi-select</MenuItem>
            </Select>
          </FormControl>
          {renderSettingValue(newSetting as TeamSetting)}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveSetting} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TeamSettings; 