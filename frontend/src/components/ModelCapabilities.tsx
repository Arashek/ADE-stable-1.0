import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  TextField
} from '@mui/material';
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  PrivacyTip as PrivacyIcon,
  Psychology as PsychologyIcon,
  AccessibilityNew as AccessibilityIcon,
  Eco as EcoIcon,
  Groups as GroupsIcon,
  MonetizationOn as MonetizationIcon,
  Gavel as GavelIcon
} from '@mui/icons-material';
import {
  Sankey,
  Tooltip as ChartTooltip,
  ResponsiveContainer
} from 'recharts';

interface Capability {
  name: string;
  description: string;
  category: string;
  dependencies: string[];
  metrics: string[];
  icon: string;
}

interface ModelCapabilitiesProps {
  onCapabilityChange?: (capability: Capability) => void;
}

const ModelCapabilities: React.FC<ModelCapabilitiesProps> = ({
  onCapabilityChange
}) => {
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [selectedCapability, setSelectedCapability] = useState<Capability | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    fetchCapabilities();
    fetchCategories();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const response = await fetch('/api/models/capabilities');
      const data = await response.json();
      setCapabilities(data.capabilities);
    } catch (err) {
      setError('Failed to fetch capabilities');
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/models/capability-categories');
      const data = await response.json();
      setCategories(data.categories);
    } catch (err) {
      setError('Failed to fetch categories');
    }
  };

  const handleOpenDialog = (capability?: Capability) => {
    setSelectedCapability(capability || {
      name: '',
      description: '',
      category: '',
      dependencies: [],
      metrics: [],
      icon: 'Info'
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedCapability(null);
  };

  const handleSaveCapability = async () => {
    if (!selectedCapability) return;

    try {
      const response = await fetch('/api/models/capabilities', {
        method: selectedCapability.name ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedCapability),
      });

      if (!response.ok) {
        throw new Error('Failed to save capability');
      }

      fetchCapabilities();
      handleCloseDialog();
      onCapabilityChange?.(selectedCapability);
    } catch (err) {
      setError('Failed to save capability');
    }
  };

  const handleDeleteCapability = async (name: string) => {
    try {
      const response = await fetch(`/api/models/capabilities/${name}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete capability');
      }

      fetchCapabilities();
    } catch (err) {
      setError('Failed to delete capability');
    }
  };

  const getCapabilityIcon = (icon: string) => {
    switch (icon) {
      case 'Code':
        return <CodeIcon />;
      case 'Security':
        return <SecurityIcon />;
      case 'Privacy':
        return <PrivacyIcon />;
      case 'Psychology':
        return <PsychologyIcon />;
      case 'Accessibility':
        return <AccessibilityIcon />;
      case 'Eco':
        return <EcoIcon />;
      case 'Groups':
        return <GroupsIcon />;
      case 'Monetization':
        return <MonetizationIcon />;
      case 'Gavel':
        return <GavelIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const getSankeyData = () => {
    const nodes: any[] = [];
    const links: any[] = [];
    let nodeId = 0;

    // Add categories as nodes
    categories.forEach(category => {
      nodes.push({
        name: category,
        id: nodeId++
      });
    });

    // Add capabilities as nodes and create links to categories
    capabilities.forEach(capability => {
      nodes.push({
        name: capability.name,
        id: nodeId++
      });

      const categoryNode = nodes.find(n => n.name === capability.category);
      if (categoryNode) {
        links.push({
          source: categoryNode.id,
          target: nodeId - 1,
          value: 1
        });
      }

      // Add dependency links
      capability.dependencies.forEach(dep => {
        const depNode = nodes.find(n => n.name === dep);
        if (depNode) {
          links.push({
            source: depNode.id,
            target: nodeId - 1,
            value: 0.5
          });
        }
      });
    });

    return { nodes, links };
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Model Capabilities</Typography>
            <Box>
              <Tooltip title="Refresh Capabilities">
                <IconButton onClick={fetchCapabilities}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Add Capability">
                <IconButton onClick={() => handleOpenDialog()}>
                  <AddIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Grid>

        {/* Error Alert */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}

        {/* Capability Visualization */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Capability Relationships
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <Sankey
                  data={getSankeyData()}
                  node={{ fill: '#8884d8' }}
                  link={{ stroke: '#8884d8', strokeOpacity: 0.3 }}
                  nodePadding={50}
                  nodeThickness={18}
                  linkCurvature={0.5}
                  iterations={32}
                >
                  <ChartTooltip />
                </Sankey>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Capabilities List */}
        <Grid item xs={12}>
          <Paper>
            <List>
              {capabilities.map((capability, index) => (
                <React.Fragment key={capability.name}>
                  <ListItem
                    secondaryAction={
                      <Box>
                        <Tooltip title="Edit">
                          <IconButton
                            edge="end"
                            onClick={() => handleOpenDialog(capability)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            edge="end"
                            onClick={() => handleDeleteCapability(capability.name)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                  >
                    <ListItemIcon>
                      {getCapabilityIcon(capability.icon)}
                    </ListItemIcon>
                    <ListItemText
                      primary={capability.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {capability.description}
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            <Chip
                              label={capability.category}
                              size="small"
                              color="primary"
                            />
                            {capability.dependencies.map((dep) => (
                              <Chip
                                key={dep}
                                label={dep}
                                size="small"
                                color="secondary"
                              />
                            ))}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < capabilities.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Capability Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedCapability?.name ? 'Edit Capability' : 'New Capability'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                value={selectedCapability?.name || ''}
                onChange={(e) => setSelectedCapability(prev => prev ? { ...prev, name: e.target.value } : null)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={selectedCapability?.description || ''}
                onChange={(e) => setSelectedCapability(prev => prev ? { ...prev, description: e.target.value } : null)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={selectedCapability?.category || ''}
                  onChange={(e) => setSelectedCapability(prev => prev ? { ...prev, category: e.target.value } : null)}
                  label="Category"
                >
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Icon</InputLabel>
                <Select
                  value={selectedCapability?.icon || 'Info'}
                  onChange={(e) => setSelectedCapability(prev => prev ? { ...prev, icon: e.target.value } : null)}
                  label="Icon"
                >
                  <MenuItem value="Code">Code</MenuItem>
                  <MenuItem value="Security">Security</MenuItem>
                  <MenuItem value="Privacy">Privacy</MenuItem>
                  <MenuItem value="Psychology">Psychology</MenuItem>
                  <MenuItem value="Accessibility">Accessibility</MenuItem>
                  <MenuItem value="Eco">Eco</MenuItem>
                  <MenuItem value="Groups">Groups</MenuItem>
                  <MenuItem value="Monetization">Monetization</MenuItem>
                  <MenuItem value="Gavel">Gavel</MenuItem>
                  <MenuItem value="Info">Info</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Dependencies</InputLabel>
                <Select
                  multiple
                  value={selectedCapability?.dependencies || []}
                  onChange={(e) => setSelectedCapability(prev => prev ? { ...prev, dependencies: e.target.value as string[] } : null)}
                  label="Dependencies"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as string[]).map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {capabilities.map((cap) => (
                    <MenuItem key={cap.name} value={cap.name}>
                      {cap.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Metrics</InputLabel>
                <Select
                  multiple
                  value={selectedCapability?.metrics || []}
                  onChange={(e) => setSelectedCapability(prev => prev ? { ...prev, metrics: e.target.value as string[] } : null)}
                  label="Metrics"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as string[]).map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  <MenuItem value="accuracy">Accuracy</MenuItem>
                  <MenuItem value="latency">Latency</MenuItem>
                  <MenuItem value="throughput">Throughput</MenuItem>
                  <MenuItem value="cost">Cost</MenuItem>
                  <MenuItem value="reliability">Reliability</MenuItem>
                  <MenuItem value="scalability">Scalability</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveCapability}
            variant="contained"
            startIcon={<SaveIcon />}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelCapabilities; 