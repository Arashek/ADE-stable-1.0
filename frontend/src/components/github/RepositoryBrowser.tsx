import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Folder as FolderIcon,
  Description as FileIcon,
  Search as SearchIcon,
  Code as CodeIcon,
  Star as StarIcon,
  AccountTree as BranchIcon,
} from '@mui/icons-material';

interface Repository {
  id: string;
  name: string;
  fullName: string;
  description: string;
  stars: number;
  defaultBranch: string;
  language: string;
  private: boolean;
}

interface RepositoryBrowserProps {
  onRepositorySelect?: (repository: Repository) => void;
}

const RepositoryBrowser: React.FC<RepositoryBrowserProps> = ({
  onRepositorySelect,
}) => {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      // TODO: Fetch repositories from GitHub API
      const mockData: Repository[] = [
        {
          id: '1',
          name: 'ade-platform',
          fullName: 'org/ade-platform',
          description: 'Autonomous Development Environment Platform',
          stars: 42,
          defaultBranch: 'main',
          language: 'TypeScript',
          private: false,
        },
        {
          id: '2',
          name: 'example-repo',
          fullName: 'org/example-repo',
          description: 'Example repository for testing',
          stars: 10,
          defaultBranch: 'master',
          language: 'Python',
          private: true,
        },
      ];
      setRepositories(mockData);
    } catch (err) {
      setError('Failed to fetch repositories');
    } finally {
      setLoading(false);
    }
  };

  const filteredRepositories = repositories.filter((repo) =>
    repo.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRepositoryClick = (repository: Repository) => {
    if (onRepositorySelect) {
      onRepositorySelect(repository);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          GitHub Repositories
        </Typography>

        <TextField
          fullWidth
          placeholder="Search repositories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
      </Box>

      <List sx={{ flexGrow: 1, overflow: 'auto' }}>
        {filteredRepositories.map((repo) => (
          <ListItem
            key={repo.id}
            disablePadding
            secondaryAction={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton size="small" edge="end">
                  <StarIcon />
                </IconButton>
                <Typography variant="body2">{repo.stars}</Typography>
                <IconButton size="small" edge="end">
                  <BranchIcon />
                </IconButton>
              </Box>
            }
          >
            <ListItemButton onClick={() => handleRepositoryClick(repo)}>
              <ListItemIcon>
                {repo.private ? <FolderIcon /> : <CodeIcon />}
              </ListItemIcon>
              <ListItemText
                primary={repo.name}
                secondary={
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Typography variant="body2" component="span">
                      {repo.description}
                    </Typography>
                    <Chip
                      size="small"
                      label={repo.language}
                      sx={{ ml: 1 }}
                    />
                  </Box>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default RepositoryBrowser; 