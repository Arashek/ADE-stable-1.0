import React, { useState } from 'react';
import { DesignSystem } from '../../types/design';
import { Button, Alert, Box, Typography, TextField, Paper } from '@mui/material';

interface FigmaIntegrationProps {
  onFileSelect: (fileKey: string) => void;
  onComponentSelect: (componentKey: string) => void;
  onStyleSelect: (styleKey: string) => void;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
  onFinalize: (design: DesignSystem) => void;
  designAgent: any;
}

/**
 * Simplified design integration component that replaces the Figma integration
 * Focuses on the core ADE platform functionality for the multi-agent architecture
 */
export const FigmaIntegration: React.FC<FigmaIntegrationProps> = ({
  onFileSelect,
  onComponentSelect,
  onStyleSelect,
  onDesignUpdate,
  onFinalize,
  designAgent,
}) => {
  const [designName, setDesignName] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleCreateDesign = async () => {
    try {
      setLoading(true);
      
      // Use the design agent to create a basic design system
      // This leverages the multi-agent architecture of ADE
      const basicDesign: DesignSystem = {
        id: `design-${Date.now()}`,
        name: designName || 'Basic Design System',
        version: '1.0.0',
        components: [],
        styles: [],
        pages: [],
        metadata: {
          description: 'A basic design system created with ADE',
          createdBy: 'ADE Platform',
          lastModified: new Date().toISOString(),
          version: '1.0.0',
          name: designName || 'Basic Design System',
          integrations: {}
        }
      };
      
      // Simulate agent interaction
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      onFinalize(basicDesign);
    } catch (error) {
      console.error('Error creating design system:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Paper sx={{ p: 3, m: 2 }}>
      <Typography variant="h6" gutterBottom>
        Design System Integration
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        External design integrations have been simplified to focus on the core ADE platform 
        functionality and prepare for cloud deployment on cloudev.ai.
      </Alert>
      
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Design System Name"
          value={designName}
          onChange={(e) => setDesignName(e.target.value)}
          margin="normal"
          variant="outlined"
        />
      </Box>
      
      <Button 
        variant="contained" 
        color="primary"
        onClick={handleCreateDesign}
        disabled={loading}
      >
        {loading ? 'Creating...' : 'Create Basic Design System'}
      </Button>
    </Paper>
  );
};