import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Switch,
  FormControlLabel,
  Slider,
  Chip
} from '@mui/material';
import { ExtendedUserPreferences } from '../../../../core/models/agent/types';

interface UserPreferencesProps {
  preferences: ExtendedUserPreferences;
  onUpdate: (updates: Partial<ExtendedUserPreferences>) => void;
}

export const UserPreferences: React.FC<UserPreferencesProps> = ({
  preferences,
  onUpdate
}) => {
  const handlePreferenceUpdate = (updates: Partial<ExtendedUserPreferences>) => {
    onUpdate({
      ...preferences,
      ...updates
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        User Preferences
      </Typography>

      <Grid container spacing={3}>
        {/* Development Environment */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Development Environment" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your development environment:
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>IDE Theme</InputLabel>
                <Select
                  label="IDE Theme"
                  defaultValue={preferences.ideTheme}
                  onChange={(e) => handlePreferenceUpdate({ ideTheme: e.target.value as 'light' | 'dark' | 'system' })}
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="system">System</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.autoSave}
                    onChange={(e) => handlePreferenceUpdate({ autoSave: e.target.checked })}
                  />
                }
                label="Enable auto-save"
                sx={{ mb: 2 }}
              />
              <Typography gutterBottom>Font Size</Typography>
              <Slider
                value={preferences.fontSize}
                min={12}
                max={24}
                step={1}
                onChange={(_, value) => handlePreferenceUpdate({ fontSize: value as number })}
                valueLabelDisplay="auto"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Code Style */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Code Style" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your code style preferences:
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Indentation</InputLabel>
                <Select
                  label="Indentation"
                  defaultValue={preferences.indentation}
                  onChange={(e) => handlePreferenceUpdate({ indentation: e.target.value as 'spaces' | 'tabs' })}
                >
                  <MenuItem value="spaces">Spaces</MenuItem>
                  <MenuItem value="tabs">Tabs</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Indentation Size"
                type="number"
                defaultValue={preferences.indentationSize}
                onChange={(e) => handlePreferenceUpdate({ indentationSize: parseInt(e.target.value) })}
                sx={{ mb: 2 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.formatOnSave}
                    onChange={(e) => handlePreferenceUpdate({ formatOnSave: e.target.checked })}
                  />
                }
                label="Format on save"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Git Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Git Configuration" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your Git preferences:
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.gitAutoCommit}
                    onChange={(e) => handlePreferenceUpdate({ gitAutoCommit: e.target.checked })}
                  />
                }
                label="Enable auto-commit"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Commit Message Template"
                defaultValue={preferences.commitMessageTemplate}
                onChange={(e) => handlePreferenceUpdate({ commitMessageTemplate: e.target.value })}
                sx={{ mb: 2 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.gitPushOnCommit}
                    onChange={(e) => handlePreferenceUpdate({ gitPushOnCommit: e.target.checked })}
                  />
                }
                label="Push on commit"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Preferences */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Notification Preferences" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your notification settings:
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences.notifications.enabled}
                    onChange={(e) => handlePreferenceUpdate({
                      notifications: {
                        ...preferences.notifications,
                        enabled: e.target.checked
                      }
                    })}
                  />
                }
                label="Enable notifications"
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth>
                <InputLabel>Notification Level</InputLabel>
                <Select
                  label="Notification Level"
                  defaultValue={preferences.notifications.level}
                  onChange={(e) => handlePreferenceUpdate({
                    notifications: {
                      ...preferences.notifications,
                      level: e.target.value as 'all' | 'important' | 'none'
                    }
                  })}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="important">Important Only</MenuItem>
                  <MenuItem value="none">None</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Keyboard Shortcuts */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Keyboard Shortcuts" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your keyboard shortcuts:
              </Typography>
              <List>
                {preferences.keyboardShortcuts.map((shortcut) => (
                  <React.Fragment key={shortcut.action}>
                    <ListItem>
                      <ListItemText
                        primary={shortcut.action}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Key: {shortcut.key}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Description: {shortcut.description}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Language Preferences */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Language Preferences" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your language preferences:
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>Preferred Languages</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {preferences.languages.map((lang) => (
                    <Chip
                      key={lang}
                      label={lang}
                      onDelete={() => handlePreferenceUpdate({
                        languages: preferences.languages.filter((l) => l !== lang)
                      })}
                    />
                  ))}
                </Box>
              </Box>
              <FormControl fullWidth>
                <InputLabel>Default Language</InputLabel>
                <Select
                  label="Default Language"
                  defaultValue={preferences.defaultLanguage}
                  onChange={(e) => handlePreferenceUpdate({ defaultLanguage: e.target.value as string })}
                >
                  {preferences.languages.map((lang) => (
                    <MenuItem key={lang} value={lang}>
                      {lang}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 