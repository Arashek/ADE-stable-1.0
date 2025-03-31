import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Tooltip,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Collapse,
  Checkbox,
  Menu,
  FormGroup,
  FormLabel,
  FormHelperText,
  Badge,
  Avatar,
  Tabs,
  Tab,
  CardHeader,
  CardActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  History as HistoryIcon,
  Security as SecurityIcon,
  Business as BusinessIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  Block as BlockIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  AccessTime as AccessTimeIcon,
  Activity as ActivityIcon,
} from '@mui/icons-material';

// Mock data - Replace with API calls
const mockUsers = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    organization: 'Acme Corp',
    tier: 'Enterprise',
    status: 'Active',
    lastLogin: '2024-03-15',
    permissions: ['admin', 'write', 'read'],
  },
  // Add more mock users...
];

const mockOrganizations = [
  {
    id: 1,
    name: 'Acme Corp',
    users: 25,
    tier: 'Enterprise',
    status: 'Active',
    createdAt: '2024-01-01',
  },
  // Add more mock organizations...
];

const tiers = ['Basic', 'Premium', 'Enterprise'];
const statuses = ['Active', 'Suspended', 'Pending'];
const permissions = ['admin', 'write', 'read', 'view'];

// User Management Component
const UserManagement = () => {
  const [users, setUsers] = useState(mockUsers);
  const [organizations, setOrganizations] = useState(mockOrganizations);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [showUserDialog, setShowUserDialog] = useState(false);
  const [showOrgDialog, setShowOrgDialog] = useState(false);
  const [showHistoryDialog, setShowHistoryDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [expandedUser, setExpandedUser] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  const [bulkActionAnchorEl, setBulkActionAnchorEl] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [filters, setFilters] = useState({
    tier: 'all',
    status: 'all',
    organization: 'all',
    lastLogin: 'all',
  });
  const [userActivity, setUserActivity] = useState({
    activeUsers: 45,
    newUsers: 12,
    suspendedUsers: 3,
    totalUsers: 60,
  });

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setShowUserDialog(true);
  };

  const handleEditOrg = (org) => {
    setSelectedOrg(org);
    setShowOrgDialog(true);
  };

  const handleSaveUser = () => {
    // Implement save logic
    setShowUserDialog(false);
    setNotification({
      open: true,
      message: 'User updated successfully',
      severity: 'success',
    });
  };

  const handleSaveOrg = () => {
    // Implement save logic
    setShowOrgDialog(false);
    setNotification({
      open: true,
      message: 'Organization updated successfully',
      severity: 'success',
    });
  };

  const handleToggleUserExpand = (userId) => {
    setExpandedUser(expandedUser === userId ? null : userId);
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedUsers(users.map(user => user.id));
    } else {
      setSelectedUsers([]);
    }
  };

  const handleSelectUser = (userId) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleBulkAction = (action) => {
    // Implement bulk action logic
    setBulkActionAnchorEl(null);
    setNotification({
      open: true,
      message: `Bulk action "${action}" applied to ${selectedUsers.length} users`,
      severity: 'success',
    });
  };

  const handleFilterChange = (filter, value) => {
    setFilters(prev => ({ ...prev, [filter]: value }));
    setFilterAnchorEl(null);
  };

  const filteredUsers = users.filter(user => {
    if (filters.tier !== 'all' && user.tier !== filters.tier) return false;
    if (filters.status !== 'all' && user.status !== filters.status) return false;
    if (filters.organization !== 'all' && user.organization !== filters.organization) return false;
    return true;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        User Management
      </Typography>

      {/* Activity Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ActivityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Active Users</Typography>
              </Box>
              <Typography variant="h4">{userActivity.activeUsers}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PersonIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">New Users</Typography>
              </Box>
              <Typography variant="h4">{userActivity.newUsers}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BlockIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Suspended</Typography>
              </Box>
              <Typography variant="h4">{userActivity.suspendedUsers}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <GroupIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Users</Typography>
              </Box>
              <Typography variant="h4">{userActivity.totalUsers}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="All Users" />
          <Tab label="Active Users" />
          <Tab label="Suspended Users" />
          <Tab label="Pending Approval" />
        </Tabs>
      </Paper>

      {/* Search and Filter Section */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search users..."
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Button
              variant="outlined"
              startIcon={<FilterListIcon />}
              onClick={(e) => setFilterAnchorEl(e.currentTarget)}
              sx={{ mr: 2 }}
            >
              Filters
            </Button>
            <Button
              variant="outlined"
              startIcon={<MoreVertIcon />}
              onClick={(e) => setBulkActionAnchorEl(e.currentTarget)}
              disabled={selectedUsers.length === 0}
              sx={{ mr: 2 }}
            >
              Bulk Actions
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowUserDialog(true)}
            >
              Add User
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Users Table */}
      <Paper sx={{ mb: 3 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selectedUsers.length > 0 && selectedUsers.length < users.length}
                    checked={selectedUsers.length === users.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Organization</TableCell>
                <TableCell>Tier</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers
                .filter((user) =>
                  user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  user.email.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((user) => (
                  <React.Fragment key={user.id}>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedUsers.includes(user.id)}
                          onChange={() => handleSelectUser(user.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 1 }}>{user.name[0]}</Avatar>
                          {user.name}
                        </Box>
                      </TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.organization}</TableCell>
                      <TableCell>
                        <Chip label={user.tier} color="primary" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.status}
                          color={user.status === 'Active' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <AccessTimeIcon sx={{ mr: 0.5, fontSize: '1rem' }} />
                          {user.lastLogin}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Edit">
                          <IconButton onClick={() => handleEditUser(user)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View History">
                          <IconButton onClick={() => setShowHistoryDialog(true)}>
                            <HistoryIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                        <IconButton onClick={() => handleToggleUserExpand(user.id)}>
                          {expandedUser === user.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell colSpan={8} sx={{ py: 0 }}>
                        <Collapse in={expandedUser === user.id} timeout="auto" unmountOnExit>
                          <Box sx={{ p: 2 }}>
                            <Grid container spacing={2}>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" gutterBottom>
                                  Permissions
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                  {user.permissions.map((permission) => (
                                    <Chip key={permission} label={permission} size="small" />
                                  ))}
                                </Box>
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" gutterBottom>
                                  Recent Activity
                                </Typography>
                                <List dense>
                                  <ListItem>
                                    <ListItemText
                                      primary="Last Login"
                                      secondary={user.lastLogin}
                                    />
                                  </ListItem>
                                  <ListItem>
                                    <ListItemText
                                      primary="Account Created"
                                      secondary="2024-01-15"
                                    />
                                  </ListItem>
                                </List>
                              </Grid>
                            </Grid>
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredUsers.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={() => setFilterAnchorEl(null)}
      >
        <MenuItem>
          <FormControl fullWidth>
            <InputLabel>Tier</InputLabel>
            <Select
              value={filters.tier}
              onChange={(e) => handleFilterChange('tier', e.target.value)}
            >
              <MenuItem value="all">All Tiers</MenuItem>
              {tiers.map((tier) => (
                <MenuItem key={tier} value={tier}>
                  {tier}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </MenuItem>
        <MenuItem>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              {statuses.map((status) => (
                <MenuItem key={status} value={status}>
                  {status}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </MenuItem>
      </Menu>

      {/* Bulk Actions Menu */}
      <Menu
        anchorEl={bulkActionAnchorEl}
        open={Boolean(bulkActionAnchorEl)}
        onClose={() => setBulkActionAnchorEl(null)}
      >
        <MenuItem onClick={() => handleBulkAction('activate')}>
          <CheckIcon sx={{ mr: 1 }} />
          Activate Selected
        </MenuItem>
        <MenuItem onClick={() => handleBulkAction('suspend')}>
          <BlockIcon sx={{ mr: 1 }} />
          Suspend Selected
        </MenuItem>
        <MenuItem onClick={() => handleBulkAction('delete')}>
          <DeleteIcon sx={{ mr: 1 }} />
          Delete Selected
        </MenuItem>
      </Menu>

      {/* Organizations Section */}
      <Paper>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            <BusinessIcon sx={{ mr: 1 }} />
            Organizations
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowOrgDialog(true)}
          >
            Add Organization
          </Button>
        </Box>
        <Divider />
        <List>
          {organizations.map((org) => (
            <ListItem key={org.id}>
              <ListItemText
                primary={org.name}
                secondary={`${org.users} users • ${org.tier} Tier • Created ${org.createdAt}`}
              />
              <ListItemSecondaryAction>
                <Tooltip title="Edit">
                  <IconButton onClick={() => handleEditOrg(org)}>
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton color="error">
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Edit User Dialog */}
      <Dialog open={showUserDialog} onClose={() => setShowUserDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <PersonIcon sx={{ mr: 1 }} />
          {selectedUser ? 'Edit User' : 'Add New User'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                defaultValue={selectedUser?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                defaultValue={selectedUser?.email}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Organization</InputLabel>
                <Select defaultValue={selectedUser?.organization}>
                  {organizations.map((org) => (
                    <MenuItem key={org.id} value={org.name}>
                      {org.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Tier</InputLabel>
                <Select defaultValue={selectedUser?.tier}>
                  {tiers.map((tier) => (
                    <MenuItem key={tier} value={tier}>
                      {tier}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select defaultValue={selectedUser?.status}>
                  {statuses.map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Permissions
              </Typography>
              {permissions.map((permission) => (
                <FormControlLabel
                  key={permission}
                  control={
                    <Switch
                      defaultChecked={selectedUser?.permissions.includes(permission)}
                    />
                  }
                  label={permission}
                />
              ))}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUserDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveUser} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Organization Dialog */}
      <Dialog open={showOrgDialog} onClose={() => setShowOrgDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <BusinessIcon sx={{ mr: 1 }} />
          {selectedOrg ? 'Edit Organization' : 'Add New Organization'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Organization Name"
                defaultValue={selectedOrg?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Tier</InputLabel>
                <Select defaultValue={selectedOrg?.tier}>
                  {tiers.map((tier) => (
                    <MenuItem key={tier} value={tier}>
                      {tier}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select defaultValue={selectedOrg?.status}>
                  {statuses.map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowOrgDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveOrg} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={showHistoryDialog} onClose={() => setShowHistoryDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <HistoryIcon sx={{ mr: 1 }} />
          Account History
        </DialogTitle>
        <DialogContent>
          <List>
            <ListItem>
              <ListItemText
                primary="Tier Changed"
                secondary="Upgraded to Enterprise Tier"
                secondaryTypographyProps={{ color: 'success.main' }}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Permissions Updated"
                secondary="Added admin access"
                secondaryTypographyProps={{ color: 'info.main' }}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Status Changed"
                secondary="Account suspended"
                secondaryTypographyProps={{ color: 'error.main' }}
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistoryDialog(false)}>Close</Button>
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
    </Box>
  );
};

export default UserManagement; 