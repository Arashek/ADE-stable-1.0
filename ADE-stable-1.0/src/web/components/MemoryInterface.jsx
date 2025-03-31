import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Tooltip,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  Share as ShareIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Add as AddIcon,
  Memory as MemoryIcon,
  Psychology as PsychologyIcon,
  History as HistoryIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

const MemoryInterface = ({ orchestrator }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [memoryStats, setMemoryStats] = useState(null);
  const [expertiseData, setExpertiseData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMemoryStats();
    loadExpertiseData();
  }, []);

  const loadMemoryStats = async () => {
    try {
      setLoading(true);
      const stats = await orchestrator.getMemoryStats();
      setMemoryStats(stats);
    } catch (err) {
      setError('Failed to load memory statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadExpertiseData = async () => {
    try {
      setLoading(true);
      const expertise = await orchestrator.getAgentExpertise();
      setExpertiseData(expertise);
    } catch (err) {
      setError('Failed to load expertise data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const results = await orchestrator.searchKnowledge(searchQuery);
      setSearchResults(results);
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async (entryId) => {
    try {
      setLoading(true);
      await orchestrator.shareKnowledge(entryId);
      // Refresh search results
      handleSearch();
    } catch (err) {
      setError('Failed to share knowledge');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (entry) => {
    setSelectedEntry(entry);
    setEditContent(entry.content);
    setEditDialogOpen(true);
  };

  const handleSaveEdit = async () => {
    try {
      setLoading(true);
      await orchestrator.updateKnowledge(selectedEntry.id, editContent);
      setEditDialogOpen(false);
      handleSearch();
    } catch (err) {
      setError('Failed to update knowledge');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this entry?')) return;

    try {
      setLoading(true);
      await orchestrator.deleteKnowledge(entryId);
      handleSearch();
    } catch (err) {
      setError('Failed to delete knowledge');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const renderMemoryStats = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Memory Statistics
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Total Entries
            </Typography>
            <Typography variant="h4">
              {memoryStats?.total_entries || 0}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="textSecondary">
              Active Agents
            </Typography>
            <Typography variant="h4">
              {memoryStats?.total_agents || 0}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" color="textSecondary">
              Average Entries per Agent
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(memoryStats?.average_entries_per_agent || 0) * 100}
              sx={{ mt: 1 }}
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderExpertiseData = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Agent Expertise
        </Typography>
        <List>
          {Object.entries(expertiseData).map(([domain, level]) => (
            <ListItem key={domain}>
              <ListItemText
                primary={domain}
                secondary={`Expertise Level: ${(level * 100).toFixed(1)}%`}
              />
              <LinearProgress
                variant="determinate"
                value={level * 100}
                sx={{ width: 100 }}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const renderSearchResults = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', mb: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search knowledge..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <IconButton onClick={handleSearch} sx={{ ml: 1 }}>
            <SearchIcon />
          </IconButton>
        </Box>

        {loading ? (
          <LinearProgress />
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <List>
            {searchResults.map((entry) => (
              <ListItem key={entry.id} divider>
                <ListItemText
                  primary={entry.topic}
                  secondary={
                    <>
                      <Typography variant="body2" color="textSecondary">
                        {entry.content}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {entry.tags.map((tag) => (
                          <Chip
                            key={tag}
                            label={tag}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                        ))}
                      </Box>
                    </>
                  }
                />
                <ListItemSecondaryAction>
                  <Tooltip title="Share">
                    <IconButton
                      edge="end"
                      onClick={() => handleShare(entry.id)}
                      sx={{ mr: 1 }}
                    >
                      <ShareIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton
                      edge="end"
                      onClick={() => handleEdit(entry)}
                      sx={{ mr: 1 }}
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton
                      edge="end"
                      onClick={() => handleDelete(entry.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Memory Interface
      </Typography>

      <Tabs
        value={activeTab}
        onChange={(e, newValue) => setActiveTab(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab icon={<SearchIcon />} label="Search" />
        <Tab icon={<MemoryIcon />} label="Statistics" />
        <Tab icon={<PsychologyIcon />} label="Expertise" />
        <Tab icon={<HistoryIcon />} label="History" />
      </Tabs>

      {activeTab === 0 && renderSearchResults()}
      {activeTab === 1 && renderMemoryStats()}
      {activeTab === 2 && renderExpertiseData()}
      {activeTab === 3 && (
        <Typography variant="body1">
          History view coming soon...
        </Typography>
      )}

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit Knowledge Entry</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveEdit}
            variant="contained"
            disabled={loading}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MemoryInterface; 