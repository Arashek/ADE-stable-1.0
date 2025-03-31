import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Avatar,
  Grid,
  TextField,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  Alert,
  Skeleton,
  Chip,
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  Email as EmailIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  Settings as SettingsIcon,
  Language as LanguageIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import UnifiedChat from '../components/shared/UnifiedChat';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar: string;
  githubUsername?: string;
  role: string;
  joinDate: string;
  preferredLanguages: string[];
  stats: {
    projects: number;
    commits: number;
    pullRequests: number;
  };
  settings: {
    emailNotifications: boolean;
    desktopNotifications: boolean;
    darkMode: boolean;
    autoSave: boolean;
  };
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editedProfile, setEditedProfile] = useState<Partial<UserProfile>>({});
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      // TODO: Fetch profile from API
      const mockData: UserProfile = {
        id: '1',
        name: 'John Doe',
        email: 'john.doe@example.com',
        avatar: 'https://mui.com/static/images/avatar/1.jpg',
        githubUsername: 'johndoe',
        role: 'Developer',
        joinDate: '2024-01-15',
        preferredLanguages: ['TypeScript', 'Python', 'Go'],
        stats: {
          projects: 12,
          commits: 342,
          pullRequests: 28,
        },
        settings: {
          emailNotifications: true,
          desktopNotifications: true,
          darkMode: false,
          autoSave: true,
        },
      };
      setProfile(mockData);
      setEditedProfile(mockData);
    } catch (err) {
      setError('Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      // TODO: Save profile via API
      setProfile((prev) => ({ ...prev, ...editedProfile } as UserProfile));
      setEditMode(false);
    } catch (err) {
      setError('Failed to save profile');
    }
  };

  const handleSettingChange = (setting: keyof UserProfile['settings']) => {
    if (!profile) return;
    
    setProfile((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        settings: {
          ...prev.settings,
          [setting]: !prev.settings[setting],
        },
      };
    });
  };

  const handleSendMessage = (message: string, threadId?: string) => {
    // TODO: Implement message sending to backend
    console.log('Sending message:', message, 'to thread:', threadId);
  };

  const handleCreateThread = (title: string, type: string) => {
    // TODO: Implement thread creation
    console.log('Creating thread:', title, 'of type:', type);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', gap: 3 }}>
          <Skeleton variant="circular" width={120} height={120} />
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" sx={{ fontSize: '2rem' }} width={200} />
            <Skeleton variant="text" sx={{ fontSize: '1rem' }} width={150} />
          </Box>
        </Box>
      </Container>
    );
  }

  if (!profile) return null;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', gap: 3, mb: 4 }}>
              <Avatar
                src={profile.avatar}
                sx={{ width: 120, height: 120 }}
              />
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Box>
                    {editMode ? (
                      <TextField
                        value={editedProfile.name}
                        onChange={(e) =>
                          setEditedProfile((prev) => ({ ...prev, name: e.target.value }))
                        }
                        sx={{ mb: 1 }}
                      />
                    ) : (
                      <Typography variant="h4" gutterBottom>
                        {profile.name}
                      </Typography>
                    )}
                    <Typography variant="body1" color="text.secondary">
                      {profile.role} · Joined {profile.joinDate}
                    </Typography>
                  </Box>
                  <Box>
                    {editMode ? (
                      <>
                        <Button
                          variant="contained"
                          onClick={handleSaveProfile}
                          sx={{ mr: 1 }}
                        >
                          Save
                        </Button>
                        <Button onClick={() => setEditMode(false)}>Cancel</Button>
                      </>
                    ) : (
                      <Button
                        variant="outlined"
                        onClick={() => setEditMode(true)}
                      >
                        Edit Profile
                      </Button>
                    )}
                  </Box>
                </Box>

                <Box sx={{ mt: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item>
                      <Chip
                        icon={<GitHubIcon />}
                        label={profile.githubUsername}
                        variant="outlined"
                        component="a"
                        href={`https://github.com/${profile.githubUsername}`}
                        target="_blank"
                        clickable
                      />
                    </Grid>
                    <Grid item>
                      <Chip
                        icon={<EmailIcon />}
                        label={profile.email}
                        variant="outlined"
                      />
                    </Grid>
                  </Grid>
                </Box>
              </Box>
            </Box>

            <Paper sx={{ p: 3, mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Recent Activity</Typography>
                <Button
                  startIcon={<ChatIcon />}
                  onClick={() => setShowChat(!showChat)}
                >
                  {showChat ? 'Hide Chat' : 'Show Chat'}
                </Button>
              </Box>
              {showChat ? (
                <Box sx={{ height: 500 }}>
                  <UnifiedChat
                    onSendMessage={handleSendMessage}
                    onCreateThread={handleCreateThread}
                    showThreads
                    currentAgent={{
                      id: 'personal-assistant',
                      name: 'Personal Assistant',
                      type: 'agent',
                      capabilities: ['code', 'planning', 'review'],
                    }}
                  />
                </Box>
              ) : (
                <List>
                  {/* Add recent activity items here */}
                  <ListItem>
                    <ListItemIcon>
                      <GitHubIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Committed to project/repo"
                      secondary="2 hours ago"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <CodeIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Created new project"
                      secondary="5 hours ago"
                    />
                  </ListItem>
                </List>
              )}
            </Paper>
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Preferred Languages
            </Typography>
            <Box sx={{ mb: 3 }}>
              {profile.preferredLanguages.map((lang) => (
                <Chip
                  key={lang}
                  icon={<LanguageIcon />}
                  label={lang}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>
              Settings
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <EmailIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Email Notifications"
                  secondary="Receive email notifications for important updates"
                />
                <Switch
                  edge="end"
                  checked={profile.settings.emailNotifications}
                  onChange={() => handleSettingChange('emailNotifications')}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <NotificationsIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Desktop Notifications"
                  secondary="Show desktop notifications"
                />
                <Switch
                  edge="end"
                  checked={profile.settings.desktopNotifications}
                  onChange={() => handleSettingChange('desktopNotifications')}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <SettingsIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Auto Save"
                  secondary="Automatically save changes"
                />
                <Switch
                  edge="end"
                  checked={profile.settings.autoSave}
                  onChange={() => handleSettingChange('autoSave')}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Statistics
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <CodeIcon />
                </ListItemIcon>
                <ListItemText
                  primary={profile.stats.projects}
                  secondary="Projects"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <GitHubIcon />
                </ListItemIcon>
                <ListItemText
                  primary={profile.stats.commits}
                  secondary="Commits"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <GitHubIcon />
                </ListItemIcon>
                <ListItemText
                  primary={profile.stats.pullRequests}
                  secondary="Pull Requests"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Profile; 