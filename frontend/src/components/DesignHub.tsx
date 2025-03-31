import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
}));

interface DesignHubProps {
  projectId?: string;
  initialDesign?: any;
  onGenerateCode?: (design: any) => void;
  onSaveDesign?: (design: any) => void;
}

export const DesignHub: React.FC<DesignHubProps> = ({ 
  projectId,
  initialDesign,
  onGenerateCode,
  onSaveDesign
}) => {
  const [currentDesign, setCurrentDesign] = useState(initialDesign || {
    name: 'New Design',
    components: [],
    styles: [],
    layout: {}
  });

  const handleSave = () => {
    if (onSaveDesign) {
      onSaveDesign(currentDesign);
    }
  };

  const handleGenerateCode = () => {
    if (onGenerateCode) {
      onGenerateCode(currentDesign);
    }
  };

  return (
    <Box sx={{ height: '100%', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        {projectId ? `Project: ${projectId}` : 'New Design'}
      </Typography>
      <Typography variant="body1" paragraph>
        Welcome to the Design Hub. This is a simplified version of the design interface.
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Design Canvas
            </Typography>
            <Box 
              sx={{ 
                flex: 1, 
                border: '1px dashed grey', 
                borderRadius: 1, 
                p: 2,
                mb: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Design canvas will be displayed here
              </Typography>
            </Box>
          </StyledPaper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Components
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                No components added yet
              </Typography>
            </Box>
            
            <Box sx={{ mt: 'auto', pt: 2, display: 'flex', gap: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleSave}
              >
                Save Design
              </Button>
              <Button 
                variant="outlined"
                onClick={handleGenerateCode}
              >
                Generate Code
              </Button>
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Box>
  );
};
