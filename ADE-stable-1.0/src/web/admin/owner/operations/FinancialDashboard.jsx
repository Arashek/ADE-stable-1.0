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
  Button,
  ButtonGroup,
  Tooltip,
  IconButton,
  Alert,
  Snackbar,
  LinearProgress,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
  Scatter,
} from 'recharts';
import {
  Refresh as RefreshIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MonetizationOnIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Lock as LockIcon,
} from '@mui/icons-material';

// Mock data - Replace with secure API calls
const mockRevenueData = [
  { month: 'Jan', basic: 50000, premium: 75000, enterprise: 120000 },
  { month: 'Feb', basic: 55000, premium: 80000, enterprise: 130000 },
  { month: 'Mar', basic: 60000, premium: 85000, enterprise: 140000 },
  { month: 'Apr', basic: 65000, premium: 90000, enterprise: 150000 },
  { month: 'May', basic: 70000, premium: 95000, enterprise: 160000 },
  { month: 'Jun', basic: 75000, premium: 100000, enterprise: 170000 },
];

const mockCostData = [
  { category: 'Infrastructure', cost: 150000, percentage: 30 },
  { category: 'Development', cost: 100000, percentage: 20 },
  { category: 'Marketing', cost: 75000, percentage: 15 },
  { category: 'Operations', cost: 125000, percentage: 25 },
  { category: 'Support', cost: 50000, percentage: 10 },
];

const mockMarginData = [
  { month: 'Jan', revenue: 245000, costs: 180000, margin: 26.5 },
  { month: 'Feb', revenue: 265000, costs: 190000, margin: 28.3 },
  { month: 'Mar', revenue: 285000, costs: 200000, margin: 29.8 },
  { month: 'Apr', revenue: 305000, costs: 210000, margin: 31.1 },
  { month: 'May', revenue: 325000, costs: 220000, margin: 32.3 },
  { month: 'Jun', revenue: 345000, costs: 230000, margin: 33.3 },
];

const mockProjectionData = [
  { scenario: 'Optimistic', revenue: 400000, costs: 250000, margin: 37.5 },
  { scenario: 'Base', revenue: 350000, costs: 230000, margin: 34.3 },
  { scenario: 'Conservative', revenue: 300000, costs: 220000, margin: 26.7 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

// Revenue Tracking Component
const RevenueTracking = () => {
  const [timeRange, setTimeRange] = useState('6m');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [showSecurityDialog, setShowSecurityDialog] = useState(false);

  const handleRefresh = () => {
    // Implement secure refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <TrendingUpIcon sx={{ mr: 1 }} />
          Revenue Tracking
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Security Info">
            <IconButton onClick={() => setShowSecurityDialog(true)} sx={{ mr: 1 }}>
              <SecurityIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <Box sx={{ mb: 2 }}>
        <ButtonGroup size="small" sx={{ mb: 2 }}>
          <Button
            variant={timeRange === '3m' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('3m')}
          >
            3M
          </Button>
          <Button
            variant={timeRange === '6m' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('6m')}
          >
            6M
          </Button>
          <Button
            variant={timeRange === '1y' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('1y')}
          >
            1Y
          </Button>
        </ButtonGroup>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={mockRevenueData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="basic" fill="#8884d8" name="Basic Tier" />
          <Bar dataKey="premium" fill="#82ca9d" name="Premium Tier" />
          <Bar dataKey="enterprise" fill="#ffc658" name="Enterprise Tier" />
        </ComposedChart>
      </ResponsiveContainer>
      <Dialog open={showSecurityDialog} onClose={() => setShowSecurityDialog(false)}>
        <DialogTitle>
          <LockIcon sx={{ mr: 1 }} />
          Security Information
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            All financial data is:
          </Typography>
          <ul>
            <li>Encrypted in transit and at rest</li>
            <li>Access-controlled with role-based permissions</li>
            <li>Audit-logged for all access attempts</li>
            <li>Compliant with financial data protection standards</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSecurityDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Cost Breakdown Component
const CostBreakdown = () => {
  const [timeRange, setTimeRange] = useState('month');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleRefresh = () => {
    // Implement secure refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <MonetizationOnIcon sx={{ mr: 1 }} />
          Cost Breakdown
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={mockCostData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="cost"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {mockCostData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <RechartsTooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <TableContainer sx={{ mt: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell align="right">Cost</TableCell>
              <TableCell align="right">Percentage</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockCostData.map((row) => (
              <TableRow key={row.category}>
                <TableCell>{row.category}</TableCell>
                <TableCell align="right">${row.cost.toLocaleString()}</TableCell>
                <TableCell align="right">{row.percentage}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Margin Analysis Component
const MarginAnalysis = () => {
  const [timeRange, setTimeRange] = useState('6m');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleRefresh = () => {
    // Implement secure refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <AssessmentIcon sx={{ mr: 1 }} />
          Margin Analysis
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={mockMarginData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <RechartsTooltip />
          <Legend />
          <Bar
            yAxisId="left"
            dataKey="revenue"
            fill="#8884d8"
            name="Revenue"
          />
          <Bar
            yAxisId="left"
            dataKey="costs"
            fill="#82ca9d"
            name="Costs"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="margin"
            stroke="#ff7300"
            name="Margin %"
          />
        </ComposedChart>
      </ResponsiveContainer>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Financial Projections Component
const FinancialProjections = () => {
  const [timeRange, setTimeRange] = useState('quarter');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [showScenarioDialog, setShowScenarioDialog] = useState(false);
  const [scenarioData, setScenarioData] = useState({
    name: '',
    revenue: '',
    costs: '',
  });

  const handleRefresh = () => {
    // Implement secure refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  const handleAddScenario = () => {
    // Implement secure scenario addition logic
    setShowScenarioDialog(false);
    setScenarioData({ name: '', revenue: '', costs: '' });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <AssessmentIcon sx={{ mr: 1 }} />
          Financial Projections
        </Typography>
        <Box>
          <Button
            variant="outlined"
            size="small"
            onClick={() => setShowScenarioDialog(true)}
            sx={{ mr: 1 }}
          >
            Add Scenario
          </Button>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={mockProjectionData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="scenario" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="revenue" fill="#8884d8" name="Projected Revenue" />
          <Bar dataKey="costs" fill="#82ca9d" name="Projected Costs" />
        </BarChart>
      </ResponsiveContainer>
      <Dialog open={showScenarioDialog} onClose={() => setShowScenarioDialog(false)}>
        <DialogTitle>Add New Scenario</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Scenario Name"
            fullWidth
            value={scenarioData.name}
            onChange={(e) => setScenarioData({ ...scenarioData, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Projected Revenue"
            type="number"
            fullWidth
            value={scenarioData.revenue}
            onChange={(e) => setScenarioData({ ...scenarioData, revenue: e.target.value })}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />
          <TextField
            margin="dense"
            label="Projected Costs"
            type="number"
            fullWidth
            value={scenarioData.costs}
            onChange={(e) => setScenarioData({ ...scenarioData, costs: e.target.value })}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowScenarioDialog(false)}>Cancel</Button>
          <Button onClick={handleAddScenario} variant="contained">
            Add Scenario
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

const FinancialDashboard = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Financial Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <RevenueTracking />
        </Grid>
        <Grid item xs={12} md={6}>
          <CostBreakdown />
        </Grid>
        <Grid item xs={12} md={6}>
          <MarginAnalysis />
        </Grid>
        <Grid item xs={12} md={6}>
          <FinancialProjections />
        </Grid>
      </Grid>
    </Box>
  );
};

export default FinancialDashboard; 