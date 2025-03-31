import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { waitlistStore } from '../../../core/storage/waitlist_store';

const WaitlistManager = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selected, setSelected] = useState([]);
  const [orderBy, setOrderBy] = useState('created_at');
  const [order, setOrder] = useState('desc');
  const [stats, setStats] = useState(null);
  const [inviteDialog, setInviteDialog] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [inviteMessage, setInviteMessage] = useState('');

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/waitlist');
      if (!response.ok) throw new Error('Failed to fetch requests');
      const data = await response.json();
      setRequests(data.requests);
      setStats(data.stats);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      setSelected(requests.map((request) => request.id));
    } else {
      setSelected([]);
    }
  };

  const handleClick = (id) => {
    const selectedIndex = selected.indexOf(id);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, id);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1)
      );
    }

    setSelected(newSelected);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleInvite = async (request) => {
    setSelectedRequest(request);
    setInviteDialog(true);
  };

  const handleSendInvite = async () => {
    try {
      const response = await fetch(`/api/admin/waitlist/${selectedRequest.id}/invite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inviteMessage }),
      });

      if (!response.ok) throw new Error('Failed to send invitation');
      
      await fetchRequests();
      setInviteDialog(false);
      setInviteMessage('');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleApprove = async (id) => {
    try {
      const response = await fetch(`/api/admin/waitlist/${id}/approve`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to approve request');
      
      await fetchRequests();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReject = async (id) => {
    try {
      const response = await fetch(`/api/admin/waitlist/${id}/reject`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to reject request');
      
      await fetchRequests();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleBulkApprove = async () => {
    try {
      const response = await fetch('/api/admin/waitlist/bulk-approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: selected }),
      });

      if (!response.ok) throw new Error('Failed to approve requests');
      
      await fetchRequests();
      setSelected([]);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleBulkReject = async () => {
    try {
      const response = await fetch('/api/admin/waitlist/bulk-reject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: selected }),
      });

      if (!response.ok) throw new Error('Failed to reject requests');
      
      await fetchRequests();
      setSelected([]);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {stats && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Waitlist Statistics
          </Typography>
          <Box display="flex" gap={4}>
            <Typography>Total: {stats.total}</Typography>
            <Typography>Pending: {stats.pending}</Typography>
            <Typography>Approved: {stats.approved}</Typography>
            <Typography>Rejected: {stats.rejected}</Typography>
          </Box>
        </Paper>
      )}

      <Paper>
        <Box p={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Early Access Requests</Typography>
            <Box>
              {selected.length > 0 && (
                <>
                  <Button
                    color="primary"
                    onClick={handleBulkApprove}
                    startIcon={<CheckIcon />}
                    sx={{ mr: 1 }}
                  >
                    Approve Selected
                  </Button>
                  <Button
                    color="error"
                    onClick={handleBulkReject}
                    startIcon={<CloseIcon />}
                  >
                    Reject Selected
                  </Button>
                </>
              )}
              <IconButton onClick={fetchRequests}>
                <RefreshIcon />
              </IconButton>
            </Box>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selected.length > 0 && selected.length < requests.length}
                      checked={requests.length > 0 && selected.length === requests.length}
                      onChange={handleSelectAllClick}
                    />
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'email'}
                      direction={orderBy === 'email' ? order : 'asc'}
                      onClick={() => handleRequestSort('email')}
                    >
                      Email
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Company</TableCell>
                  <TableCell>Use Case</TableCell>
                  <TableCell>Position</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'created_at'}
                      direction={orderBy === 'created_at' ? order : 'asc'}
                      onClick={() => handleRequestSort('created_at')}
                    >
                      Submitted
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((request) => (
                    <TableRow
                      key={request.id}
                      hover
                      selected={selected.indexOf(request.id) !== -1}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selected.indexOf(request.id) !== -1}
                          onChange={() => handleClick(request.id)}
                        />
                      </TableCell>
                      <TableCell>{request.email}</TableCell>
                      <TableCell>{request.name || '-'}</TableCell>
                      <TableCell>{request.company || '-'}</TableCell>
                      <TableCell>{request.use_case || '-'}</TableCell>
                      <TableCell>{request.position}</TableCell>
                      <TableCell>{request.status}</TableCell>
                      <TableCell>
                        {new Date(request.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {request.status === 'pending' && (
                          <>
                            <Tooltip title="Approve">
                              <IconButton
                                color="primary"
                                onClick={() => handleApprove(request.id)}
                              >
                                <CheckIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject">
                              <IconButton
                                color="error"
                                onClick={() => handleReject(request.id)}
                              >
                                <CloseIcon />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                        {request.status === 'approved' && (
                          <Tooltip title="Send Invitation">
                            <IconButton
                              color="primary"
                              onClick={() => handleInvite(request)}
                            >
                              <SendIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={requests.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Box>
      </Paper>

      <Dialog open={inviteDialog} onClose={() => setInviteDialog(false)}>
        <DialogTitle>Send Invitation</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Invitation Message"
            fullWidth
            multiline
            rows={4}
            value={inviteMessage}
            onChange={(e) => setInviteMessage(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteDialog(false)}>Cancel</Button>
          <Button onClick={handleSendInvite} color="primary">
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WaitlistManager; 