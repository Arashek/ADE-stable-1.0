import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    Alert,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { Code as CodeIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const StyledPaper = styled(Paper)(({ theme }) => ({
    margin: theme.spacing(2),
    padding: theme.spacing(2),
    height: 'calc(100vh - 100px)',
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(3),
}));

/**
 * Simplified DesignAnalyzer component that focuses on the core functionality
 * needed for local testing before cloud deployment
 */
export const DesignAnalyzer: React.FC = () => {
    const navigate = useNavigate();

    const handleGoToCodeEditor = () => {
        navigate('/editor');
    };

    return (
        <StyledPaper elevation={3}>
            <Typography variant="h5" gutterBottom>
                Design Analyzer
            </Typography>

            <Alert severity="info">
                The Design Analyzer has been simplified to focus on the core multi-agent architecture 
                for local testing before cloud deployment on cloudev.ai.
            </Alert>

            <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                    Design Analysis Overview
                </Typography>
                <Typography paragraph>
                    The ADE platform's design analysis functionality has been streamlined to focus on the essential
                    multi-agent architecture that powers the platform. The specialized agents for architecture, 
                    code generation, testing, debugging, and optimization are the core components that differentiate
                    ADE from other platforms.
                </Typography>
                <Typography paragraph>
                    For local testing purposes, you can proceed directly to the code editor to work with the
                    multi-agent system.
                </Typography>
                <Button 
                    variant="contained" 
                    color="primary" 
                    startIcon={<CodeIcon />}
                    onClick={handleGoToCodeEditor}
                    sx={{ mt: 2 }}
                >
                    Go to Code Editor
                </Button>
            </Box>
        </StyledPaper>
    );
};