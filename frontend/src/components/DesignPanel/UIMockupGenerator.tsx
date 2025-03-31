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
    Chip,
    Paper,
    Typography,
    IconButton,
} from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { DesignRequest } from '../../types/design';
import { useProjectContext } from '../../hooks/useProjectContext';

interface UIMockupGeneratorProps {
    onGenerate: (request: DesignRequest) => Promise<any>;
}

export const UIMockupGenerator: React.FC<UIMockupGeneratorProps> = ({ onGenerate }) => {
    const { projectContext } = useProjectContext();
    const [requirements, setRequirements] = useState<string[]>([]);
    const [newRequirement, setNewRequirement] = useState('');
    const [style, setStyle] = useState({
        colorScheme: '',
        typography: '',
        spacing: '',
        layout: '',
    });
    const [dimensions, setDimensions] = useState({
        width: 1024,
        height: 1024,
    });
    const [loading, setLoading] = useState(false);
    const [preview, setPreview] = useState<string | null>(null);

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

    const handleDimensionsChange = (field: string) => (event: any) => {
        const value = parseInt(event.target.value, 10);
        if (!isNaN(value)) {
            setDimensions({ ...dimensions, [field]: value });
        }
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        try {
            const request: DesignRequest = {
                id: crypto.randomUUID(),
                requirements,
                projectContext,
                style,
                dimensions,
            };

            const response = await onGenerate(request);
            setPreview(response.mockup);
        } catch (error) {
            console.error('Error generating mockup:', error);
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
                            label="Add Requirement"
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
                            Requirements
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
                                <InputLabel>Typography</InputLabel>
                                <Select
                                    value={style.typography}
                                    onChange={handleStyleChange('typography')}
                                    label="Typography"
                                >
                                    <MenuItem value="modern">Modern</MenuItem>
                                    <MenuItem value="classic">Classic</MenuItem>
                                    <MenuItem value="playful">Playful</MenuItem>
                                    <MenuItem value="technical">Technical</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                    </Grid>

                    <Grid container spacing={2} sx={{ mt: 2 }}>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                type="number"
                                label="Width"
                                value={dimensions.width}
                                onChange={handleDimensionsChange('width')}
                                InputProps={{ inputProps: { min: 1 } }}
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                fullWidth
                                type="number"
                                label="Height"
                                value={dimensions.height}
                                onChange={handleDimensionsChange('height')}
                                InputProps={{ inputProps: { min: 1 } }}
                            />
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
                        {loading ? 'Generating...' : 'Generate UI Mockup'}
                    </Button>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper 
                        sx={{ 
                            p: 2, 
                            height: '100%', 
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        {preview ? (
                            <img 
                                src={`data:image/png;base64,${preview}`}
                                alt="Generated UI Mockup"
                                style={{ maxWidth: '100%', maxHeight: '100%' }}
                            />
                        ) : (
                            <Typography color="textSecondary">
                                Generated mockup will appear here
                            </Typography>
                        )}
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}; 