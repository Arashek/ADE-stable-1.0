import React, { useState } from 'react';
import {
    Box,
    Paper,
    Tabs,
    Tab,
    Typography,
    CircularProgress,
    Alert,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { UIMockupGenerator } from './UIMockupGenerator';
import { DesignAnalyzer } from './DesignAnalyzer';
import { AssetGenerator } from './AssetGenerator';
import { DesignRequest, DesignResponse, DesignFeedback } from '../../types/design';
import { useDesignAgent } from '../../hooks/useDesignAgent';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel = (props: TabPanelProps) => {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`design-tabpanel-${index}`}
            aria-labelledby={`design-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
};

const StyledPaper = styled(Paper)(({ theme }) => ({
    margin: theme.spacing(2),
    padding: theme.spacing(2),
    height: 'calc(100vh - 100px)',
    display: 'flex',
    flexDirection: 'column',
}));

export const DesignPanel: React.FC = () => {
    const [activeTab, setActiveTab] = useState(0);
    const { 
        generateMockup,
        analyzeDesign,
        generateAssets,
        loading,
        error 
    } = useDesignAgent();

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setActiveTab(newValue);
    };

    const handleGenerateMockup = async (request: DesignRequest) => {
        try {
            const response = await generateMockup(request);
            // Handle successful mockup generation
            return response;
        } catch (err) {
            console.error('Error generating mockup:', err);
            throw err;
        }
    };

    const handleAnalyzeDesign = async (design: any) => {
        try {
            const feedback = await analyzeDesign(design);
            // Handle successful design analysis
            return feedback;
        } catch (err) {
            console.error('Error analyzing design:', err);
            throw err;
        }
    };

    const handleGenerateAssets = async (request: DesignRequest) => {
        try {
            const assets = await generateAssets(request);
            // Handle successful asset generation
            return assets;
        } catch (err) {
            console.error('Error generating assets:', err);
            throw err;
        }
    };

    return (
        <StyledPaper elevation={3}>
            <Typography variant="h5" gutterBottom>
                Design Assistant
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Tabs
                value={activeTab}
                onChange={handleTabChange}
                aria-label="design panel tabs"
                sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
                <Tab label="UI Mockup" />
                <Tab label="Design Analysis" />
                <Tab label="Asset Generation" />
            </Tabs>

            {loading && (
                <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center',
                    height: '100%' 
                }}>
                    <CircularProgress />
                </Box>
            )}

            {!loading && (
                <>
                    <TabPanel value={activeTab} index={0}>
                        <UIMockupGenerator onGenerate={handleGenerateMockup} />
                    </TabPanel>

                    <TabPanel value={activeTab} index={1}>
                        <DesignAnalyzer onAnalyze={handleAnalyzeDesign} />
                    </TabPanel>

                    <TabPanel value={activeTab} index={2}>
                        <AssetGenerator onGenerate={handleGenerateAssets} />
                    </TabPanel>
                </>
            )}
        </StyledPaper>
    );
}; 