import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, CircularProgress, Paper } from '@mui/material';
import { styled } from '@mui/material/styles';
import { DesignHub } from '../components/DesignHub';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';

const StyledContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
}));

interface DesignHubPageParams {
  projectId?: string;
}

const DesignHubPage: React.FC = () => {
  const { projectId } = useParams<DesignHubPageParams>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);

  // Handle code generation result
  const handleGenerateCode = (design: any) => {
    console.log('Generated code from design:', design);
    // We could navigate to editor with generated code
    // navigate(`/editor/${projectId}`, { state: { generatedCode: code } });
  };

  // Handle save design
  const handleSaveDesign = (design: any) => {
    console.log('Saved design:', design);
    // We could handle design saving to backend here
  };

  return (
    <StyledContainer>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <Button 
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/command-hub')}
          sx={{ mr: 2 }}
        >
          Back to Command Hub
        </Button>
        <Typography variant="h4">
          Design Hub {projectId ? `- Project: ${projectId}` : ''}
        </Typography>
      </Box>
      
      <Paper sx={{ p: 2, height: 'calc(100% - 80px)' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <DesignHub 
            projectId={projectId}
            onGenerateCode={handleGenerateCode}
            onSaveDesign={handleSaveDesign}
            initialDesign={undefined}
          />
        )}
      </Paper>
    </StyledContainer>
  );
};

export default DesignHubPage;
