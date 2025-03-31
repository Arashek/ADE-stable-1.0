import React, { useState } from 'react';
import {
    Box,
    TextField,
    Button,
    Grid,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Paper,
    Typography,
    IconButton,
    ImageList,
    ImageListItem,
    Chip,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { DesignRequest } from '../../types/design';
import { useProjectContext } from '../../hooks/useProjectContext';

interface AssetGeneratorProps {
    onGenerate: (request: DesignRequest) => Promise<string[]>;
}

export const AssetGenerator: React.FC<AssetGeneratorProps> = ({ onGenerate }) => {
    const { projectContext } = useProjectContext();
    const [requirements, setRequirements] = useState<string[]>([]);
    const [newRequirement, setNewRequirement] = useState('');
    const [style, setStyle] = useState({
        colorScheme: '',
        layout: '',
    });
    const [format, setFormat] = useState<'svg' | 'png' | 'jpg'>('svg');
    const [loading, setLoading] = useState(false);
    const [generatedAssets, setGeneratedAssets] = useState<string[]>([]);

    const handleAddRequirement = () => {
        if (newRequirement.trim()) {
            setRequirements([...requirements, newRequirement.trim()]);
            setNewRequirement('');
        }
    };

    const handleRemoveRequirement = (index: number) => {
        setRequirements(requirements.filter((_, i) => i !== index));
    };

    const handleStyleChange = (field: string) => (event: any) => {
        setStyle({ ...style, [field]: event.target.value });
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        try {
            const request: DesignRequest = {
                id: crypto.randomUUID(),
                requirements: [],
                projectContext,
                style,
                assetRequirements: requirements,
                assetFormat: format,
            };

            const assets = await onGenerate(request);
            setGeneratedAssets(assets);
        } catch (error) {
            console.error('Error generating assets:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Box sx={{ mb: 3 }}>
                        <TextField
                            fullWidth
                            label="Add Asset Requirement"
                            value={newRequirement}
                            onChange={(e) => setNewRequirement(e.target.value)}
                            InputProps={{
                                endAdornment: (
                                    <IconButton 
                                        onClick={handleAddRequirement}
                                        disabled={!newRequirement.trim()}
                                    >
                                        <AddIcon />
                                    </IconButton>
                                ),
                            }}
                        />
                    </Box>

                    <Paper sx={{ p: 2, mb: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            Asset Requirements
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {requirements.map((req, index) => (
                                <Chip
                                    key={index}
                                    label={req}
                                    onDelete={() => handleRemoveRequirement(index)}
                                    color="primary"
                                />
                            ))}
                        </Box>
                    </Paper>

                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <FormControl fullWidth>
                                <InputLabel>Color Scheme</InputLabel>
                                <Select
                                    value={style.colorScheme}
                                    onChange={handleStyleChange('colorScheme')}
                                    label="Color Scheme"
                                >
                                    <MenuItem value="light">Light</MenuItem>
                                    <MenuItem value="dark">Dark</MenuItem>
                                    <MenuItem value="colorful">Colorful</MenuItem>
                                    <MenuItem value="minimal">Minimal</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={6}>
                            <FormControl fullWidth>
                                <InputLabel>Format</InputLabel>
                                <Select
                                    value={format}
                                    onChange={(e) => setFormat(e.target.value as 'svg' | 'png' | 'jpg')}
                                    label="Format"
                                >
                                    <MenuItem value="svg">SVG</MenuItem>
                                    <MenuItem value="png">PNG</MenuItem>
                                    <MenuItem value="jpg">JPG</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>

                    <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        type="submit"
                        disabled={loading || requirements.length === 0}
                        sx={{ mt: 3 }}
                    >
                        {loading ? 'Generating...' : 'Generate Assets'}
                    </Button>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                        {generatedAssets.length > 0 ? (
                            <ImageList cols={2} gap={8}>
                                {generatedAssets.map((asset, index) => (
                                    <ImageListItem key={index}>
                                        <img
                                            src={format === 'svg' ? asset : `data:image/${format};base64,${asset}`}
                                            alt={`Generated asset ${index + 1}`}
                                            loading="lazy"
                                            style={{ width: '100%', height: 'auto' }}
                                        />
                                        <Button
                                            fullWidth
                                            variant="outlined"
                                            size="small"
                                            onClick={() => {
                                                const link = document.createElement('a');
                                                link.href = format === 'svg' ? asset : `data:image/${format};base64,${asset}`;
                                                link.download = `asset-${index + 1}.${format}`;
                                                link.click();
                                            }}
                                            sx={{ mt: 1 }}
                                        >
                                            Download
                                        </Button>
                                    </ImageListItem>
                                ))}
                            </ImageList>
                        ) : (
                            <Typography color="textSecondary" align="center">
                                Generated assets will appear here
                            </Typography>
                        )}
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}; 