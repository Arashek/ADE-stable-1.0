import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CompareArrows as CompareIcon,
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
} from '@mui/icons-material';

interface CodeDiff {
  id: string;
  file: string;
  oldCode: string;
  newCode: string;
  timestamp: string;
  author: string;
}

const CodeEvolution: React.FC = () => {
  const [currentDiff] = useState<CodeDiff>({
    id: '1',
    file: 'src/components/CommandHub.tsx',
    oldCode: `import React from 'react';
import { Box, Grid, Paper } from '@mui/material';

const CommandHub: React.FC = () => {
  return (
    <Box>
      <Grid container>
        <Grid item xs={12}>
          <Paper>Old Content</Paper>
        </Grid>
      </Grid>
    </Box>
  );
};`,
    newCode: `import React from 'react';
import { Box, Grid, Paper, ThemeProvider } from '@mui/material';

const CommandHub: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ flexGrow: 1 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Paper>New Content</Paper>
          </Grid>
        </Grid>
      </Box>
    </ThemeProvider>
  );
};`,
    timestamp: '2024-03-20 14:30',
    author: 'Code Generator',
  });

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Code Evolution</Typography>
        <Box>
          <Tooltip title="Previous Change">
            <IconButton size="small">
              <PrevIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Next Change">
            <IconButton size="small">
              <NextIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ flex: 1 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%', bgcolor: 'background.paper' }}>
            <Typography variant="subtitle2" gutterBottom>
              Previous Version
            </Typography>
            <TextField
              multiline
              fullWidth
              value={currentDiff.oldCode}
              variant="outlined"
              InputProps={{
                readOnly: true,
                sx: {
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                },
              }}
            />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%', bgcolor: 'background.paper' }}>
            <Typography variant="subtitle2" gutterBottom>
              Current Version
            </Typography>
            <TextField
              multiline
              fullWidth
              value={currentDiff.newCode}
              variant="outlined"
              InputProps={{
                readOnly: true,
                sx: {
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                },
              }}
            />
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          {currentDiff.file} • {currentDiff.timestamp} • {currentDiff.author}
        </Typography>
        <Tooltip title="Compare Changes">
          <IconButton size="small">
            <CompareIcon />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default CodeEvolution; 