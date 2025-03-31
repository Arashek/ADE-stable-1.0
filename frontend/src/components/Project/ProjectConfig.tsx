import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  FormControlLabel,
  Switch,
  Alert,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Build as BuildIcon,
  Cloud as CloudIcon,
  Template as TemplateIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface EnvironmentVariable {
  key: string;
  value: string;
  isSecret: boolean;
}

interface Dependency {
  name: string;
  version: string;
  type: 'dependencies' | 'devDependencies';
}

interface BuildConfig {
  buildCommand: string;
  outputDirectory: string;
  environment: 'development' | 'production' | 'test';
  optimizationLevel: 'none' | 'basic' | 'advanced';
  sourceMaps: boolean;
}

interface DeploymentConfig {
  platform: 'aws' | 'azure' | 'gcp' | 'heroku' | 'custom';
  region: string;
  environment: 'staging' | 'production';
  autoDeploy: boolean;
  deploymentBranch: string;
  buildCommand: string;
  envVars: EnvironmentVariable[];
}

interface SecurityConfig {
  ssl: boolean;
  cors: {
    enabled: boolean;
    allowedOrigins: string[];
  };
  rateLimit: {
    enabled: boolean;
    maxRequests: number;
    windowMs: number;
  };
  authentication: {
    type: 'none' | 'basic' | 'jwt' | 'oauth';
    config: Record<string, any>;
  };
}

interface ProjectTemplate {
  id: string;
  name: string;
  description: string;
  type: 'frontend' | 'backend' | 'fullstack';
  framework: string;
  features: string[];
}

interface ProjectConfig {
  name: string;
  description: string;
  version: string;
  environmentVariables: EnvironmentVariable[];
  dependencies: Dependency[];
  settings: {
    autoSave: boolean;
    formatOnSave: boolean;
    lintOnSave: boolean;
    useGitHooks: boolean;
  };
  buildConfig: BuildConfig;
  deploymentConfig: DeploymentConfig;
  securityConfig: SecurityConfig;
  template: ProjectTemplate | null;
  scripts: Record<string, string>;
  engines: {
    node?: string;
    python?: string;
    java?: string;
  };
}

interface ProjectConfigProps {
  config: ProjectConfig;
  onSave: (config: ProjectConfig) => void;
  onRefresh: () => void;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`project-config-tabpanel-${index}`}
    aria-labelledby={`project-config-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const ProjectConfig: React.FC<ProjectConfigProps> = ({
  config,
  onSave,
  onRefresh,
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [editedConfig, setEditedConfig] = useState<ProjectConfig>(config);
  const [newEnvVarDialogOpen, setNewEnvVarDialogOpen] = useState(false);
  const [newDependencyDialogOpen, setNewDependencyDialogOpen] = useState(false);
  const [newEnvVar, setNewEnvVar] = useState<EnvironmentVariable>({
    key: '',
    value: '',
    isSecret: false,
  });
  const [newDependency, setNewDependency] = useState<Dependency>({
    name: '',
    version: '',
    type: 'dependencies',
  });
  const [editingEnvVar, setEditingEnvVar] = useState<EnvironmentVariable | null>(null);
  const [editingDependency, setEditingDependency] = useState<Dependency | null>(null);
  const [newScriptName, setNewScriptName] = useState('');
  const [newScriptCommand, setNewScriptCommand] = useState('');
  const [newCorsOrigin, setNewCorsOrigin] = useState('');
  const [scriptDialogOpen, setScriptDialogOpen] = useState(false);
  const [corsDialogOpen, setCorsDialogOpen] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleConfigChange = (field: keyof ProjectConfig, value: any) => {
    setEditedConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleSettingChange = (setting: keyof ProjectConfig['settings']) => {
    setEditedConfig((prev) => ({
      ...prev,
      settings: {
        ...prev.settings,
        [setting]: !prev.settings[setting],
      },
    }));
  };

  const handleAddEnvVar = () => {
    if (newEnvVar.key && newEnvVar.value) {
      setEditedConfig((prev) => ({
        ...prev,
        environmentVariables: [...prev.environmentVariables, newEnvVar],
      }));
      setNewEnvVar({ key: '', value: '', isSecret: false });
      setNewEnvVarDialogOpen(false);
    }
  };

  const handleAddDependency = () => {
    if (newDependency.name && newDependency.version) {
      setEditedConfig((prev) => ({
        ...prev,
        dependencies: [...prev.dependencies, newDependency],
      }));
      setNewDependency({ name: '', version: '', type: 'dependencies' });
      setNewDependencyDialogOpen(false);
    }
  };

  const handleDeleteEnvVar = (key: string) => {
    setEditedConfig((prev) => ({
      ...prev,
      environmentVariables: prev.environmentVariables.filter((v) => v.key !== key),
    }));
  };

  const handleDeleteDependency = (name: string) => {
    setEditedConfig((prev) => ({
      ...prev,
      dependencies: prev.dependencies.filter((d) => d.name !== name),
    }));
  };

  const handleEditEnvVar = (envVar: EnvironmentVariable) => {
    setEditingEnvVar(envVar);
    setNewEnvVar(envVar);
    setNewEnvVarDialogOpen(true);
  };

  const handleEditDependency = (dependency: Dependency) => {
    setEditingDependency(dependency);
    setNewDependency(dependency);
    setNewDependencyDialogOpen(true);
  };

  const handleSave = () => {
    onSave(editedConfig);
  };

  const handleAddScript = () => {
    if (newScriptName && newScriptCommand) {
      setEditedConfig((prev) => ({
        ...prev,
        scripts: {
          ...prev.scripts,
          [newScriptName]: newScriptCommand,
        },
      }));
      setNewScriptName('');
      setNewScriptCommand('');
      setScriptDialogOpen(false);
    }
  };

  const handleDeleteScript = (name: string) => {
    setEditedConfig((prev) => {
      const { [name]: _, ...rest } = prev.scripts;
      return { ...prev, scripts: rest };
    });
  };

  const handleAddCorsOrigin = () => {
    if (newCorsOrigin) {
      setEditedConfig((prev) => ({
        ...prev,
        securityConfig: {
          ...prev.securityConfig,
          cors: {
            ...prev.securityConfig.cors,
            allowedOrigins: [...prev.securityConfig.cors.allowedOrigins, newCorsOrigin],
          },
        },
      }));
      setNewCorsOrigin('');
      setCorsDialogOpen(false);
    }
  };

  const handleDeleteCorsOrigin = (origin: string) => {
    setEditedConfig((prev) => ({
      ...prev,
      securityConfig: {
        ...prev.securityConfig,
        cors: {
          ...prev.securityConfig.cors,
          allowedOrigins: prev.securityConfig.cors.allowedOrigins.filter((o) => o !== origin),
        },
      },
    }));
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Project Configuration</Typography>
        <Box>
          <IconButton onClick={onRefresh} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
          >
            Save Changes
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tab label="General" />
        <Tab label="Environment Variables" />
        <Tab label="Dependencies" />
        <Tab label="Build" />
        <Tab label="Deployment" />
        <Tab label="Security" />
        <Tab label="Scripts" />
        <Tab label="Settings" />
      </Tabs>

      {/* General Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Project Name"
              value={editedConfig.name}
              onChange={(e) => handleConfigChange('name', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={editedConfig.description}
              onChange={(e) => handleConfigChange('description', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Version"
              value={editedConfig.version}
              onChange={(e) => handleConfigChange('version', e.target.value)}
            />
          </Grid>
        </Grid>
      </TabPanel>

      {/* Environment Variables Tab */}
      <TabPanel value={activeTab} index={1}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setNewEnvVarDialogOpen(true)}
          >
            Add Environment Variable
          </Button>
        </Box>
        <List>
          {editedConfig.environmentVariables.map((envVar) => (
            <ListItem key={envVar.key}>
              <ListItemText
                primary={envVar.key}
                secondary={envVar.isSecret ? '********' : envVar.value}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleEditEnvVar(envVar)}
                  sx={{ mr: 1 }}
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  onClick={() => handleDeleteEnvVar(envVar.key)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </TabPanel>

      {/* Dependencies Tab */}
      <TabPanel value={activeTab} index={2}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setNewDependencyDialogOpen(true)}
          >
            Add Dependency
          </Button>
        </Box>
        <List>
          {editedConfig.dependencies.map((dependency) => (
            <ListItem key={dependency.name}>
              <ListItemText
                primary={dependency.name}
                secondary={`${dependency.version} (${dependency.type})`}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleEditDependency(dependency)}
                  sx={{ mr: 1 }}
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  onClick={() => handleDeleteDependency(dependency.name)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </TabPanel>

      {/* Build Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Build Command"
              value={editedConfig.buildConfig.buildCommand}
              onChange={(e) =>
                setEditedConfig((prev) => ({
                  ...prev,
                  buildConfig: {
                    ...prev.buildConfig,
                    buildCommand: e.target.value,
                  },
                }))
              }
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Output Directory"
              value={editedConfig.buildConfig.outputDirectory}
              onChange={(e) =>
                setEditedConfig((prev) => ({
                  ...prev,
                  buildConfig: {
                    ...prev.buildConfig,
                    outputDirectory: e.target.value,
                  },
                }))
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Environment</InputLabel>
              <Select
                value={editedConfig.buildConfig.environment}
                label="Environment"
                onChange={(e) =>
                  setEditedConfig((prev) => ({
                    ...prev,
                    buildConfig: {
                      ...prev.buildConfig,
                      environment: e.target.value as BuildConfig['environment'],
                    },
                  }))
                }
              >
                <MenuItem value="development">Development</MenuItem>
                <MenuItem value="production">Production</MenuItem>
                <MenuItem value="test">Test</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Optimization Level</InputLabel>
              <Select
                value={editedConfig.buildConfig.optimizationLevel}
                label="Optimization Level"
                onChange={(e) =>
                  setEditedConfig((prev) => ({
                    ...prev,
                    buildConfig: {
                      ...prev.buildConfig,
                      optimizationLevel: e.target.value as BuildConfig['optimizationLevel'],
                    },
                  }))
                }
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="basic">Basic</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.buildConfig.sourceMaps}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      buildConfig: {
                        ...prev.buildConfig,
                        sourceMaps: e.target.checked,
                      },
                    }))
                  }
                />
              }
              label="Generate Source Maps"
            />
          </Grid>
        </Grid>
      </TabPanel>

      {/* Deployment Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Platform</InputLabel>
              <Select
                value={editedConfig.deploymentConfig.platform}
                label="Platform"
                onChange={(e) =>
                  setEditedConfig((prev) => ({
                    ...prev,
                    deploymentConfig: {
                      ...prev.deploymentConfig,
                      platform: e.target.value as DeploymentConfig['platform'],
                    },
                  }))
                }
              >
                <MenuItem value="aws">AWS</MenuItem>
                <MenuItem value="azure">Azure</MenuItem>
                <MenuItem value="gcp">Google Cloud</MenuItem>
                <MenuItem value="heroku">Heroku</MenuItem>
                <MenuItem value="custom">Custom</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Region"
              value={editedConfig.deploymentConfig.region}
              onChange={(e) =>
                setEditedConfig((prev) => ({
                  ...prev,
                  deploymentConfig: {
                    ...prev.deploymentConfig,
                    region: e.target.value,
                  },
                }))
              }
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Environment</InputLabel>
              <Select
                value={editedConfig.deploymentConfig.environment}
                label="Environment"
                onChange={(e) =>
                  setEditedConfig((prev) => ({
                    ...prev,
                    deploymentConfig: {
                      ...prev.deploymentConfig,
                      environment: e.target.value as DeploymentConfig['environment'],
                    },
                  }))
                }
              >
                <MenuItem value="staging">Staging</MenuItem>
                <MenuItem value="production">Production</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Deployment Branch"
              value={editedConfig.deploymentConfig.deploymentBranch}
              onChange={(e) =>
                setEditedConfig((prev) => ({
                  ...prev,
                  deploymentConfig: {
                    ...prev.deploymentConfig,
                    deploymentBranch: e.target.value,
                  },
                }))
              }
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.deploymentConfig.autoDeploy}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      deploymentConfig: {
                        ...prev.deploymentConfig,
                        autoDeploy: e.target.checked,
                      },
                    }))
                  }
                />
              }
              label="Auto Deploy on Push"
            />
          </Grid>
        </Grid>
      </TabPanel>

      {/* Security Tab */}
      <TabPanel value={activeTab} index={5}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.securityConfig.ssl}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      securityConfig: {
                        ...prev.securityConfig,
                        ssl: e.target.checked,
                      },
                    }))
                  }
                />
              }
              label="Enable SSL"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.securityConfig.cors.enabled}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      securityConfig: {
                        ...prev.securityConfig,
                        cors: {
                          ...prev.securityConfig.cors,
                          enabled: e.target.checked,
                        },
                      },
                    }))
                  }
                />
              }
              label="Enable CORS"
            />
          </Grid>
          {editedConfig.securityConfig.cors.enabled && (
            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => setCorsDialogOpen(true)}
                >
                  Add Allowed Origin
                </Button>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                {editedConfig.securityConfig.cors.allowedOrigins.map((origin) => (
                  <Chip
                    key={origin}
                    label={origin}
                    onDelete={() => handleDeleteCorsOrigin(origin)}
                  />
                ))}
              </Stack>
            </Grid>
          )}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.securityConfig.rateLimit.enabled}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      securityConfig: {
                        ...prev.securityConfig,
                        rateLimit: {
                          ...prev.securityConfig.rateLimit,
                          enabled: e.target.checked,
                        },
                      },
                    }))
                  }
                />
              }
              label="Enable Rate Limiting"
            />
          </Grid>
          {editedConfig.securityConfig.rateLimit.enabled && (
            <>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Max Requests"
                  value={editedConfig.securityConfig.rateLimit.maxRequests}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      securityConfig: {
                        ...prev.securityConfig,
                        rateLimit: {
                          ...prev.securityConfig.rateLimit,
                          maxRequests: parseInt(e.target.value),
                        },
                      },
                    }))
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Window (ms)"
                  value={editedConfig.securityConfig.rateLimit.windowMs}
                  onChange={(e) =>
                    setEditedConfig((prev) => ({
                      ...prev,
                      securityConfig: {
                        ...prev.securityConfig,
                        rateLimit: {
                          ...prev.securityConfig.rateLimit,
                          windowMs: parseInt(e.target.value),
                        },
                      },
                    }))
                  }
                />
              </Grid>
            </>
          )}
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Authentication Type</InputLabel>
              <Select
                value={editedConfig.securityConfig.authentication.type}
                label="Authentication Type"
                onChange={(e) =>
                  setEditedConfig((prev) => ({
                    ...prev,
                    securityConfig: {
                      ...prev.securityConfig,
                      authentication: {
                        ...prev.securityConfig.authentication,
                        type: e.target.value as SecurityConfig['authentication']['type'],
                      },
                    },
                  }))
                }
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="basic">Basic Auth</MenuItem>
                <MenuItem value="jwt">JWT</MenuItem>
                <MenuItem value="oauth">OAuth</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Scripts Tab */}
      <TabPanel value={activeTab} index={6}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setScriptDialogOpen(true)}
          >
            Add Script
          </Button>
        </Box>
        <List>
          {Object.entries(editedConfig.scripts).map(([name, command]) => (
            <ListItem key={name}>
              <ListItemText
                primary={name}
                secondary={command}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  onClick={() => handleDeleteScript(name)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </TabPanel>

      {/* Settings Tab */}
      <TabPanel value={activeTab} index={7}>
        <List>
          <ListItem>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.settings.autoSave}
                  onChange={() => handleSettingChange('autoSave')}
                />
              }
              label="Auto Save"
            />
          </ListItem>
          <ListItem>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.settings.formatOnSave}
                  onChange={() => handleSettingChange('formatOnSave')}
                />
              }
              label="Format on Save"
            />
          </ListItem>
          <ListItem>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.settings.lintOnSave}
                  onChange={() => handleSettingChange('lintOnSave')}
                />
              }
              label="Lint on Save"
            />
          </ListItem>
          <ListItem>
            <FormControlLabel
              control={
                <Switch
                  checked={editedConfig.settings.useGitHooks}
                  onChange={() => handleSettingChange('useGitHooks')}
                />
              }
              label="Use Git Hooks"
            />
          </ListItem>
        </List>
      </TabPanel>

      {/* New/Edit Environment Variable Dialog */}
      <Dialog
        open={newEnvVarDialogOpen}
        onClose={() => setNewEnvVarDialogOpen(false)}
      >
        <DialogTitle>
          {editingEnvVar ? 'Edit Environment Variable' : 'New Environment Variable'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Key"
            fullWidth
            value={newEnvVar.key}
            onChange={(e) => setNewEnvVar((prev) => ({ ...prev, key: e.target.value }))}
          />
          <TextField
            margin="dense"
            label="Value"
            fullWidth
            type={newEnvVar.isSecret ? 'password' : 'text'}
            value={newEnvVar.value}
            onChange={(e) => setNewEnvVar((prev) => ({ ...prev, value: e.target.value }))}
          />
          <FormControlLabel
            control={
              <Switch
                checked={newEnvVar.isSecret}
                onChange={(e) =>
                  setNewEnvVar((prev) => ({ ...prev, isSecret: e.target.checked }))
                }
              />
            }
            label="Secret"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewEnvVarDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddEnvVar} variant="contained">
            {editingEnvVar ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* New/Edit Dependency Dialog */}
      <Dialog
        open={newDependencyDialogOpen}
        onClose={() => setNewDependencyDialogOpen(false)}
      >
        <DialogTitle>
          {editingDependency ? 'Edit Dependency' : 'New Dependency'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Package Name"
            fullWidth
            value={newDependency.name}
            onChange={(e) =>
              setNewDependency((prev) => ({ ...prev, name: e.target.value }))
            }
          />
          <TextField
            margin="dense"
            label="Version"
            fullWidth
            value={newDependency.version}
            onChange={(e) =>
              setNewDependency((prev) => ({ ...prev, version: e.target.value }))
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={newDependency.type === 'devDependencies'}
                onChange={(e) =>
                  setNewDependency((prev) => ({
                    ...prev,
                    type: e.target.checked ? 'devDependencies' : 'dependencies',
                  }))
                }
              />
            }
            label="Development Dependency"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewDependencyDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddDependency} variant="contained">
            {editingDependency ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Script Dialog */}
      <Dialog
        open={scriptDialogOpen}
        onClose={() => setScriptDialogOpen(false)}
      >
        <DialogTitle>Add Script</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Script Name"
            fullWidth
            value={newScriptName}
            onChange={(e) => setNewScriptName(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Command"
            fullWidth
            value={newScriptCommand}
            onChange={(e) => setNewScriptCommand(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScriptDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddScript} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add CORS Origin Dialog */}
      <Dialog
        open={corsDialogOpen}
        onClose={() => setCorsDialogOpen(false)}
      >
        <DialogTitle>Add Allowed Origin</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Origin URL"
            fullWidth
            value={newCorsOrigin}
            onChange={(e) => setNewCorsOrigin(e.target.value)}
            placeholder="https://example.com"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCorsDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddCorsOrigin} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProjectConfig; 