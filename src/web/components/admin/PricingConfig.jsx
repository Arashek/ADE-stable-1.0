import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Grid,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { FeatureFlag } from '../../../core/auth/pricing_tiers';

const PricingConfig = () => {
  const [tiers, setTiers] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTier, setEditingTier] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: 0,
    billing_period: 'monthly',
    trial_days: 0,
    is_active: true,
    features: {},
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchTiers();
  }, []);

  const fetchTiers = async () => {
    try {
      const response = await fetch('/api/admin/pricing-tiers');
      const data = await response.json();
      setTiers(data);
    } catch (err) {
      setError('Failed to fetch pricing tiers');
    }
  };

  const handleOpenDialog = (tier = null) => {
    if (tier) {
      setEditingTier(tier);
      setFormData(tier);
    } else {
      setEditingTier(null);
      setFormData({
        name: '',
        description: '',
        price: 0,
        billing_period: 'monthly',
        trial_days: 0,
        is_active: true,
        features: {},
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingTier(null);
    setFormData({
      name: '',
      description: '',
      price: 0,
      billing_period: 'monthly',
      trial_days: 0,
      is_active: true,
      features: {},
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleFeatureChange = (feature, value) => {
    setFormData(prev => ({
      ...prev,
      features: {
        ...prev.features,
        [feature]: value,
      },
    }));
  };

  const handleSubmit = async () => {
    try {
      const url = editingTier
        ? `/api/admin/pricing-tiers/${editingTier.name}`
        : '/api/admin/pricing-tiers';
      
      const method = editingTier ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to save pricing tier');
      }

      setSuccess('Pricing tier saved successfully');
      handleCloseDialog();
      fetchTiers();
    } catch (err) {
      setError('Failed to save pricing tier');
    }
  };

  const handleDelete = async (tierName) => {
    if (!window.confirm('Are you sure you want to delete this tier?')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/pricing-tiers/${tierName}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete pricing tier');
      }

      setSuccess('Pricing tier deleted successfully');
      fetchTiers();
    } catch (err) {
      setError('Failed to delete pricing tier');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Pricing Configuration</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Tier
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell>Billing Period</TableCell>
              <TableCell>Trial Days</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tiers.map((tier) => (
              <TableRow key={tier.name}>
                <TableCell>{tier.name}</TableCell>
                <TableCell>{tier.description}</TableCell>
                <TableCell align="right">${tier.price}</TableCell>
                <TableCell>{tier.billing_period}</TableCell>
                <TableCell>{tier.trial_days}</TableCell>
                <TableCell>
                  <Switch
                    checked={tier.is_active}
                    onChange={() => handleFeatureChange('is_active', !tier.is_active)}
                  />
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleOpenDialog(tier)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(tier.name)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTier ? 'Edit Pricing Tier' : 'Add New Pricing Tier'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Price"
                name="price"
                type="number"
                value={formData.price}
                onChange={handleInputChange}
                InputProps={{
                  startAdornment: '$',
                }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Billing Period"
                name="billing_period"
                select
                value={formData.billing_period}
                onChange={handleInputChange}
                SelectProps={{
                  native: true,
                }}
              >
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Trial Days"
                name="trial_days"
                type="number"
                value={formData.trial_days}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    name="is_active"
                  />
                }
                label="Active"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Features
              </Typography>
              {Object.values(FeatureFlag).map((feature) => (
                <TextField
                  key={feature}
                  fullWidth
                  label={feature}
                  type="number"
                  value={formData.features[feature] || 0}
                  onChange={(e) => handleFeatureChange(feature, Number(e.target.value))}
                  sx={{ mb: 1 }}
                />
              ))}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSubmit}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PricingConfig; 