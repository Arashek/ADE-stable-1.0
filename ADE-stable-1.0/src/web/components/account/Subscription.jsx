import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  LinearProgress,
  Card,
  CardContent,
  CardActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import {
  Check as CheckIcon,
  Close as CloseIcon,
  Upgrade as UpgradeIcon,
  CreditCard as CreditCardIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { FeatureFlag } from '../../../core/auth/pricing_tiers';

const Subscription = () => {
  const [currentTier, setCurrentTier] = useState(null);
  const [availableTiers, setAvailableTiers] = useState([]);
  const [usage, setUsage] = useState({});
  const [billingHistory, setBillingHistory] = useState([]);
  const [openPaymentDialog, setOpenPaymentDialog] = useState(false);
  const [selectedTier, setSelectedTier] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      const [tierResponse, usageResponse, historyResponse] = await Promise.all([
        fetch('/api/account/subscription'),
        fetch('/api/account/usage'),
        fetch('/api/account/billing-history'),
      ]);

      const tierData = await tierResponse.json();
      const usageData = await usageResponse.json();
      const historyData = await historyResponse.json();

      setCurrentTier(tierData.currentTier);
      setAvailableTiers(tierData.availableTiers);
      setUsage(usageData);
      setBillingHistory(historyData);
    } catch (err) {
      setError('Failed to fetch subscription data');
    }
  };

  const handleUpgrade = (tier) => {
    setSelectedTier(tier);
    setOpenPaymentDialog(true);
  };

  const handleClosePaymentDialog = () => {
    setOpenPaymentDialog(false);
    setSelectedTier(null);
  };

  const handlePaymentSubmit = async () => {
    try {
      const response = await fetch('/api/account/subscription/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tierName: selectedTier.name,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to process payment');
      }

      setSuccess('Subscription upgraded successfully');
      handleClosePaymentDialog();
      fetchSubscriptionData();
    } catch (err) {
      setError('Failed to process payment');
    }
  };

  const renderFeatureList = (tier) => {
    return Object.entries(tier.features).map(([feature, limit]) => (
      <ListItem key={feature}>
        <ListItemIcon>
          {limit.value > 0 ? <CheckIcon color="success" /> : <CloseIcon color="error" />}
        </ListItemIcon>
        <ListItemText
          primary={feature}
          secondary={limit.value > 0 ? `Limit: ${limit.value} ${limit.period}` : 'Not available'}
        />
      </ListItem>
    ));
  };

  const renderUsageProgress = (feature) => {
    const featureUsage = usage[feature];
    if (!featureUsage) return null;

    const percentage = (featureUsage.current / featureUsage.limit) * 100;
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          {feature}
        </Typography>
        <LinearProgress
          variant="determinate"
          value={Math.min(percentage, 100)}
          color={percentage > 90 ? 'error' : percentage > 75 ? 'warning' : 'primary'}
          sx={{ height: 8, borderRadius: 4 }}
        />
        <Typography variant="caption" color="text.secondary">
          {featureUsage.current} / {featureUsage.limit}
        </Typography>
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
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

      <Grid container spacing={3}>
        {/* Current Plan */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Current Plan
            </Typography>
            <Typography variant="h4" gutterBottom>
              {currentTier?.name}
            </Typography>
            <Typography variant="h5" color="primary" gutterBottom>
              ${currentTier?.price}/month
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {currentTier?.description}
            </Typography>
            <Button
              variant="outlined"
              startIcon={<CreditCardIcon />}
              onClick={() => setOpenPaymentDialog(true)}
            >
              Manage Payment
            </Button>
          </Paper>
        </Grid>

        {/* Usage Statistics */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Usage Statistics
            </Typography>
            {Object.keys(usage).map((feature) => renderUsageProgress(feature))}
          </Paper>
        </Grid>

        {/* Available Plans */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Available Plans
          </Typography>
          <Grid container spacing={2}>
            {availableTiers.map((tier) => (
              <Grid item xs={12} md={4} key={tier.name}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" gutterBottom>
                      {tier.name}
                    </Typography>
                    <Typography variant="h4" color="primary" gutterBottom>
                      ${tier.price}/month
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {tier.description}
                    </Typography>
                    <List>
                      {renderFeatureList(tier)}
                    </List>
                  </CardContent>
                  <CardActions>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<UpgradeIcon />}
                      onClick={() => handleUpgrade(tier)}
                      disabled={tier.name === currentTier?.name}
                    >
                      {tier.name === currentTier?.name ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Billing History */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Billing History
            </Typography>
            <List>
              {billingHistory.map((invoice, index) => (
                <React.Fragment key={invoice.id}>
                  <ListItem>
                    <ListItemIcon>
                      <HistoryIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={`Invoice #${invoice.id}`}
                      secondary={`${new Date(invoice.date).toLocaleDateString()} - $${invoice.amount}`}
                    />
                  </ListItem>
                  {index < billingHistory.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Payment Dialog */}
      <Dialog open={openPaymentDialog} onClose={handleClosePaymentDialog}>
        <DialogTitle>Upgrade Subscription</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            You are upgrading to the {selectedTier?.name} plan for ${selectedTier?.price}/month.
          </Typography>
          <TextField
            fullWidth
            label="Card Number"
            margin="normal"
            required
          />
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Expiry Date"
                margin="normal"
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="CVV"
                margin="normal"
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePaymentDialog}>Cancel</Button>
          <Button variant="contained" onClick={handlePaymentSubmit}>
            Process Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Subscription; 