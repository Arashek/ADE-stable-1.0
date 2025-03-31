import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Paper,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Card,
  CardContent,
  CardActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Check as CheckIcon,
  Close as CloseIcon,
  Launch as LaunchIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Group as GroupIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { FeatureFlag } from '../../../core/auth/pricing_tiers';

const EarlyAccess = () => {
  const [openSignup, setOpenSignup] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    useCase: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleOpenSignup = () => setOpenSignup(true);
  const handleCloseSignup = () => setOpenSignup(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/early-access', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit early access request');
      }

      setSuccess('Thank you for your interest! We will contact you soon.');
      handleCloseSignup();
      setFormData({
        name: '',
        email: '',
        company: '',
        useCase: '',
      });
    } catch (err) {
      setError('Failed to submit early access request');
    }
  };

  const renderFeatureComparison = () => {
    const features = Object.values(FeatureFlag);
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Feature</TableCell>
              <TableCell align="center">Free</TableCell>
              <TableCell align="center">Professional</TableCell>
              <TableCell align="center">Team</TableCell>
              <TableCell align="center">Enterprise</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {features.map((feature) => (
              <TableRow key={feature}>
                <TableCell component="th" scope="row">
                  {feature}
                </TableCell>
                <TableCell align="center">
                  {feature === FeatureFlag.PROJECTS ? '3' :
                   feature === FeatureFlag.COMPUTE_HOURS ? '50' :
                   feature === FeatureFlag.STORAGE_GB ? '5' :
                   feature === FeatureFlag.API_CALLS ? '1000' : '❌'}
                </TableCell>
                <TableCell align="center">
                  {feature === FeatureFlag.PROJECTS ? '10' :
                   feature === FeatureFlag.COMPUTE_HOURS ? '200' :
                   feature === FeatureFlag.STORAGE_GB ? '20' :
                   feature === FeatureFlag.API_CALLS ? '5000' :
                   feature === FeatureFlag.CUSTOM_DOMAINS ? '1' :
                   feature === FeatureFlag.ADVANCED_ANALYTICS ? '1' : '❌'}
                </TableCell>
                <TableCell align="center">
                  {feature === FeatureFlag.PROJECTS ? '30' :
                   feature === FeatureFlag.COMPUTE_HOURS ? '1000' :
                   feature === FeatureFlag.STORAGE_GB ? '100' :
                   feature === FeatureFlag.API_CALLS ? '20000' :
                   feature === FeatureFlag.TEAM_MEMBERS ? '5' :
                   feature === FeatureFlag.CUSTOM_DOMAINS ? '3' :
                   feature === FeatureFlag.ADVANCED_ANALYTICS ? '1' :
                   feature === FeatureFlag.PRIORITY_SUPPORT ? '1' : '❌'}
                </TableCell>
                <TableCell align="center">
                  {feature === FeatureFlag.PROJECTS ? '100' :
                   feature === FeatureFlag.COMPUTE_HOURS ? '5000' :
                   feature === FeatureFlag.STORAGE_GB ? '500' :
                   feature === FeatureFlag.API_CALLS ? '100000' :
                   feature === FeatureFlag.TEAM_MEMBERS ? '20' :
                   feature === FeatureFlag.CUSTOM_DOMAINS ? '10' :
                   feature === FeatureFlag.ADVANCED_ANALYTICS ? '1' :
                   feature === FeatureFlag.PRIORITY_SUPPORT ? '1' :
                   feature === FeatureFlag.SSO ? '1' :
                   feature === FeatureFlag.AUDIT_LOGS ? '1' : '❌'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 8,
          mb: 6,
        }}
      >
        <Container>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" gutterBottom>
                Accelerate Your Development
              </Typography>
              <Typography variant="h5" paragraph>
                The ADE platform provides a powerful, integrated environment for modern software development.
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                size="large"
                startIcon={<LaunchIcon />}
                onClick={handleOpenSignup}
              >
                Request Early Access
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                component="img"
                src="/images/hero-image.png"
                alt="ADE Platform"
                sx={{
                  width: '100%',
                  maxWidth: 500,
                  display: 'block',
                  margin: 'auto',
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container sx={{ mb: 6 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Key Features
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <SpeedIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Lightning Fast
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Optimized performance for rapid development and deployment.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <SecurityIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Enterprise Security
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Built with security best practices and compliance in mind.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <GroupIcon sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Team Collaboration
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Seamless collaboration tools for distributed teams.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Pricing Section */}
      <Container sx={{ mb: 6 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Pricing Plans
        </Typography>
        {renderFeatureComparison()}
      </Container>

      {/* Sign Up Dialog */}
      <Dialog open={openSignup} onClose={handleCloseSignup} maxWidth="sm" fullWidth>
        <DialogTitle>Request Early Access</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Company"
              name="company"
              value={formData.company}
              onChange={handleInputChange}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Use Case"
              name="useCase"
              value={formData.useCase}
              onChange={handleInputChange}
              margin="normal"
              multiline
              rows={4}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSignup}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      {error && (
        <Alert severity="error" sx={{ position: 'fixed', bottom: 16, right: 16 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ position: 'fixed', bottom: 16, right: 16 }}>
          {success}
        </Alert>
      )}
    </Box>
  );
};

export default EarlyAccess; 