import React from 'react';
import MediaProcessor from '../components/MediaProcessor';
import { Box, Container, Typography } from '@mui/material';

const MediaProcessingPage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Media Processing
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Process voice recordings and images with advanced AI capabilities.
        </Typography>
        
        <MediaProcessor />
      </Box>
    </Container>
  );
};

export default MediaProcessingPage; 