import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Avatar,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  Security as SecurityIcon,
  Email as EmailIcon,
} from '@mui/icons-material';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'developer' | 'reviewer' | 'viewer';
  avatar?: string;
  status: 'active' | 'pending' | 'inactive';
  joinedAt: string;
}

interface TeamRole {
  id: string;
  name: string;
  description: string;
  permissions: string[];
}

const defaultRoles: TeamRole[] = [
  {
    id: 'admin',
    name: 'Admin',
    description: 'Full access to all features and team management',
    permissions: ['manage_team', 'manage_roles', 'manage_projects', 'manage_settings'],
  },
  {
    id: 'developer',
    name: 'Developer',
    description: 'Can create and modify code, review changes',
    permissions: ['create_code', 'modify_code', 'review_code', 'create_branches'],
  },
  {
    id: 'reviewer',
    name: 'Reviewer',
    description: 'Can review code and provide feedback',
    permissions: ['review_code', 'comment_code', 'approve_changes'],
  },
  {
    id: 'viewer',
    name: 'Viewer',
    description: 'Can view code and documentation',
    permissions: ['view_code', 'view_docs'],
  },
];

const TeamManagement: React.FC = () => {
  const [members, setMembers] = useState<TeamMember[]>([
    {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'admin',
      status: 'active',
      joinedAt: '2024-01-01',
    },
    {
      id: '2',
      name: 'Jane Smith',
      email: 'jane@example.com',
      role: 'developer',
      status: 'active',
      joinedAt: '2024-01-02',
    },
  ]);

  const [roles, setRoles] = useState<TeamRole[]>(defaultRoles);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'member' | 'role'>('member');
  const [editingItem, setEditingItem] = useState<TeamMember | TeamRole | null>(null);
  const [newMember, setNewMember] = useState({
    name: '',
    email: '',
    role: '',
  });
  const [newRole, setNewRole] = useState({
    name: '',
    description: '',
    permissions: [] as string[],
  });

  const handleOpenDialog = (type: 'member' | 'role', item?: TeamMember | TeamRole) => {
    setDialogType(type);
    if (item) {
      setEditingItem(item);
      if (type === 'member') {
        setNewMember({
          name: (item as TeamMember).name,
          email: (item as TeamMember).email,
          role: (item as TeamMember).role,
        });
      } else {
        setNewRole({
          name: (item as TeamRole).name,
          description: (item as TeamRole).description,
          permissions: (item as TeamRole).permissions,
        });
      }
    } else {
      setEditingItem(null);
      setNewMember({ name: '', email: '', role: '' });
      setNewRole({ name: '', description: '', permissions: [] });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setNewMember({ name: '', email: '', role: '' });
    setNewRole({ name: '', description: '', permissions: [] });
  };

  const handleSaveMember = () => {
    if (editingItem) {
      setMembers(members.map(member =>
        member.id === (editingItem as TeamMember).id
          ? { ...member, ...newMember }
          : member
      ));
    } else {
      setMembers([
        ...members,
        {
          id: Date.now().toString(),
          ...newMember,
          status: 'pending',
          joinedAt: new Date().toISOString().split('T')[0],
        },
      ]);
    }
    handleCloseDialog();
  };

  const handleSaveRole = () => {
    if (editingItem) {
      setRoles(roles.map(role =>
        role.id === (editingItem as TeamRole).id
          ? { ...role, ...newRole }
          : role
      ));
    } else {
      setRoles([
        ...roles,
        {
          id: newRole.name.toLowerCase(),
          ...newRole,
        },
      ]);
    }
    handleCloseDialog();
  };

  const handleDeleteMember = (id: string) => {
    setMembers(members.filter(member => member.id !== id));
  };

  const handleDeleteRole = (id: string) => {
    setRoles(roles.filter(role => role.id !== id));
  };

  const getStatusColor = (status: TeamMember['status']) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'pending':
        return 'warning';
      case 'inactive':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Team Members Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                <GroupIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Team Members
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog('member')}
              >
                Add Member
              </Button>
            </Box>
            <List>
              {members.map((member) => (
                <ListItem key={member.id}>
                  <ListItemAvatar>
                    <Avatar src={member.avatar}>
                      <PersonIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={member.name}
                    secondary={
                      <Box>
                        <Typography component="span" variant="body2" color="text.primary">
                          {member.email}
                        </Typography>
                        <Chip
                          size="small"
                          label={member.role}
                          sx={{ ml: 1 }}
                        />
                        <Chip
                          size="small"
                          label={member.status}
                          color={getStatusColor(member.status)}
                          sx={{ ml: 1 }}
                        />
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Edit">
                      <IconButton
                        edge="end"
                        onClick={() => handleOpenDialog('member', member)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        edge="end"
                        onClick={() => handleDeleteMember(member.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Roles Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Team Roles
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog('role')}
              >
                Add Role
              </Button>
            </Box>
            <List>
              {roles.map((role) => (
                <ListItem key={role.id}>
                  <ListItemText
                    primary={role.name}
                    secondary={
                      <Box>
                        <Typography component="span" variant="body2" color="text.primary">
                          {role.description}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          {role.permissions.map((permission) => (
                            <Chip
                              key={permission}
                              size="small"
                              label={permission}
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="Edit">
                      <IconButton
                        edge="end"
                        onClick={() => handleOpenDialog('role', role)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        edge="end"
                        onClick={() => handleDeleteRole(role.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Add/Edit Member Dialog */}
      <Dialog open={openDialog && dialogType === 'member'} onClose={handleCloseDialog}>
        <DialogTitle>
          {editingItem ? 'Edit Team Member' : 'Add Team Member'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newMember.name}
            onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Email"
            type="email"
            fullWidth
            value={newMember.email}
            onChange={(e) => setNewMember({ ...newMember, email: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Role</InputLabel>
            <Select
              value={newMember.role}
              label="Role"
              onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
            >
              {roles.map((role) => (
                <MenuItem key={role.id} value={role.id}>
                  {role.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveMember} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Role Dialog */}
      <Dialog open={openDialog && dialogType === 'role'} onClose={handleCloseDialog}>
        <DialogTitle>
          {editingItem ? 'Edit Role' : 'Add Role'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={newRole.name}
            onChange={(e) => setNewRole({ ...newRole, name: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newRole.description}
            onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Permissions</InputLabel>
            <Select
              multiple
              value={newRole.permissions}
              label="Permissions"
              onChange={(e) => setNewRole({ ...newRole, permissions: e.target.value as string[] })}
            >
              <MenuItem value="manage_team">Manage Team</MenuItem>
              <MenuItem value="manage_roles">Manage Roles</MenuItem>
              <MenuItem value="manage_projects">Manage Projects</MenuItem>
              <MenuItem value="manage_settings">Manage Settings</MenuItem>
              <MenuItem value="create_code">Create Code</MenuItem>
              <MenuItem value="modify_code">Modify Code</MenuItem>
              <MenuItem value="review_code">Review Code</MenuItem>
              <MenuItem value="create_branches">Create Branches</MenuItem>
              <MenuItem value="comment_code">Comment Code</MenuItem>
              <MenuItem value="approve_changes">Approve Changes</MenuItem>
              <MenuItem value="view_code">View Code</MenuItem>
              <MenuItem value="view_docs">View Documentation</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveRole} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TeamManagement; 