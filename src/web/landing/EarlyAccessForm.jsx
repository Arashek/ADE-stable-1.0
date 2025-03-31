import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Alert,
  Paper,
  Typography,
  CircularProgress,
} from '@mui/material';

const useCases = [
  'Individual Developer',
  'Startup',
  'Enterprise',
  'Educational Institution',
  'Open Source Project',
  'Other',
];

const EarlyAccessForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    company: '',
    useCase: '',
    privacyPolicy: false,
  });
  const [status, setStatus] = useState({
    loading: false,
    success: false,
    error: null,
  });

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'privacyPolicy' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, success: false, error: null });

    try {
      const response = await fetch('/api/early-access/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to submit form');
      }

      setStatus({ loading: false, success: true, error: null });
      setFormData({
        email: '',
        name: '',
        company: '',
        useCase: '',
        privacyPolicy: false,
      });
    } catch (error) {
      setStatus({
        loading: false,
        success: false,
        error: error.message,
      });
    }
  };

  const isFormValid = () => {
    return (
      formData.email &&
      formData.email.includes('@') &&
      formData.privacyPolicy
    );
  };

  if (status.success) {
    return (
      <Paper
        elevation={3}
        sx={{
          p: 4,
          textAlign: 'center',
          maxWidth: 600,
          mx: 'auto',
        }}
      >
        <Typography variant="h5" gutterBottom>
          Thank You for Joining!
        </Typography>
        <Typography paragraph>
          We've sent a confirmation email to {formData.email}. We'll be in touch soon with your early access details.
        </Typography>
        <Button
          variant="contained"
          onClick={() => setStatus({ loading: false, success: false, error: null })}
        >
          Submit Another Request
        </Button>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={3}
      component="form"
      onSubmit={handleSubmit}
      sx={{
        p: 4,
        maxWidth: 600,
        mx: 'auto',
      }}
    >
      {status.error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {status.error}
        </Alert>
      )}

      <TextField
        fullWidth
        required
        label="Email"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        margin="normal"
        disabled={status.loading}
      />

      <TextField
        fullWidth
        label="Name (Optional)"
        name="name"
        value={formData.name}
        onChange={handleChange}
        margin="normal"
        disabled={status.loading}
      />

      <TextField
        fullWidth
        label="Company (Optional)"
        name="company"
        value={formData.company}
        onChange={handleChange}
        margin="normal"
        disabled={status.loading}
      />

      <FormControl fullWidth margin="normal">
        <InputLabel>Use Case</InputLabel>
        <Select
          name="useCase"
          value={formData.useCase}
          onChange={handleChange}
          label="Use Case"
          disabled={status.loading}
        >
          {useCases.map((useCase) => (
            <MenuItem key={useCase} value={useCase}>
              {useCase}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControlLabel
        control={
          <Checkbox
            name="privacyPolicy"
            checked={formData.privacyPolicy}
            onChange={handleChange}
            disabled={status.loading}
          />
        }
        label={
          <Typography variant="body2">
            I agree to the{' '}
            <a
              href="/privacy-policy"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'inherit' }}
            >
              Privacy Policy
            </a>{' '}
            and consent to receiving updates about CloudEV.ai
          </Typography>
        }
        sx={{ mt: 2 }}
      />

      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={!isFormValid() || status.loading}
        sx={{ mt: 3 }}
      >
        {status.loading ? (
          <CircularProgress size={24} color="inherit" />
        ) : (
          'Request Early Access'
        )}
      </Button>

      <Typography
        variant="body2"
        color="text.secondary"
        align="center"
        sx={{ mt: 2 }}
      >
        Limited spots available. We'll review your request and get back to you soon.
      </Typography>
    </Paper>
  );
};

export default EarlyAccessForm; 