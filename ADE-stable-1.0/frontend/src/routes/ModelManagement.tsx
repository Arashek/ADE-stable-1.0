import React from 'react';
import { Box, Container } from '@mui/material';
import ModelDashboard from '../components/ModelDashboard';

const ModelManagement: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <ModelDashboard />
      </Box>
    </Container>
  );
};

export default ModelManagement; 