import React, { useState } from 'react';
import { Box, Grid, Paper, Typography, useTheme } from '@mui/material';
import { styled } from '@mui/material/styles';
import CommandPanel from './CommandPanel';
import ProjectTimeline from './ProjectTimeline';
import CodeEvolution from './CodeEvolution';
import AgentCommunication from './AgentCommunication';
import RuntimePreview from './RuntimePreview';
import ChatPanel from './ChatPanel';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
}));

const CommandHub: React.FC = () => {
  const theme = useTheme();
  const [activeAgent, setActiveAgent] = useState<string | null>(null);

  return (
    <Box sx={{ flexGrow: 1, p: 3, backgroundColor: 'background.default' }}>
      <Grid container spacing={3}>
        {/* Command Input and Active Agents */}
        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Command Center
            </Typography>
            <CommandPanel onAgentSelect={setActiveAgent} />
          </StyledPaper>
        </Grid>

        {/* Project Timeline */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Project Timeline
            </Typography>
            <ProjectTimeline />
          </StyledPaper>
        </Grid>

        {/* Code Evolution View */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Code Evolution
            </Typography>
            <CodeEvolution />
          </StyledPaper>
        </Grid>

        {/* Agent Communication */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Agent Communication
            </Typography>
            <AgentCommunication activeAgent={activeAgent} />
          </StyledPaper>
        </Grid>

        {/* Runtime Preview */}
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Runtime Preview
            </Typography>
            <RuntimePreview />
          </StyledPaper>
        </Grid>

        {/* Chat Panel */}
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h5" gutterBottom>
              Project Discussion
            </Typography>
            <ChatPanel />
          </StyledPaper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CommandHub; 