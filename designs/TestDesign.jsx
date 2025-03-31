import React from 'react';
import { Button, TextField, Box, Typography } from '@mui/material';

const TestDesign = () => {
  return (
    <Box sx={{ padding: '20px' }}>
      <Typography variant="h4">Home</Typography>
      <Button variant="contained" color="primary">
        Click Me
      </Button>
      <TextField label="Name" placeholder="Enter your name" fullWidth />
    </Box>
  );
};

export default TestDesign;
