import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Switch,
    FormControlLabel,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Box,
    Typography,
    Divider,
} from '@mui/material';
import { AIAssistantSettings } from '../../interfaces/ai-assistant';

interface AIAssistantSettingsProps {
    open: boolean;
    settings: AIAssistantSettings;
    onClose: () => void;
    onSave: (settings: AIAssistantSettings) => void;
}

export const AIAssistantSettingsPanel: React.FC<AIAssistantSettingsProps> = ({
    open,
    settings,
    onClose,
    onSave,
}) => {
    const [localSettings, setLocalSettings] = React.useState<AIAssistantSettings>(settings);

    const handleChange = (field: keyof AIAssistantSettings, value: any) => {
        setLocalSettings(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleModelChange = (field: keyof typeof settings.model, value: any) => {
        setLocalSettings(prev => ({
            ...prev,
            model: {
                ...prev.model,
                [field]: value
            }
        }));
    };

    const handleFeaturesChange = (feature: keyof typeof settings.features) => {
        setLocalSettings(prev => ({
            ...prev,
            features: {
                ...prev.features,
                [feature]: !prev.features[feature]
            }
        }));
    };

    const handlePreferencesChange = (preference: keyof typeof settings.preferences, value: any) => {
        setLocalSettings(prev => ({
            ...prev,
            preferences: {
                ...prev.preferences,
                [preference]: value
            }
        }));
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>AI Assistant Settings</DialogTitle>
            <DialogContent>
                <Box sx={{ mt: 2 }}>
                    <Typography variant="h6" gutterBottom>Model Configuration</Typography>
                    <Box sx={{ display: 'grid', gap: 2, mb: 3 }}>
                        <TextField
                            label="Model"
                            value={localSettings.model.model}
                            onChange={(e) => handleModelChange('model', e.target.value)}
                            fullWidth
                        />
                        <TextField
                            label="Temperature"
                            type="number"
                            value={localSettings.model.temperature}
                            onChange={(e) => handleModelChange('temperature', parseFloat(e.target.value))}
                            inputProps={{ min: 0, max: 1, step: 0.1 }}
                            fullWidth
                        />
                        <TextField
                            label="Max Tokens"
                            type="number"
                            value={localSettings.model.maxTokens}
                            onChange={(e) => handleModelChange('maxTokens', parseInt(e.target.value))}
                            inputProps={{ min: 1, max: 4000 }}
                            fullWidth
                        />
                    </Box>

                    <Divider sx={{ my: 3 }} />

                    <Typography variant="h6" gutterBottom>Features</Typography>
                    <Box sx={{ display: 'grid', gap: 1, mb: 3 }}>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.features.codeCompletion}
                                    onChange={() => handleFeaturesChange('codeCompletion')}
                                />
                            }
                            label="Code Completion"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.features.commandSuggestions}
                                    onChange={() => handleFeaturesChange('commandSuggestions')}
                                />
                            }
                            label="Command Suggestions"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.features.errorExplanations}
                                    onChange={() => handleFeaturesChange('errorExplanations')}
                                />
                            }
                            label="Error Explanations"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.features.refactoring}
                                    onChange={() => handleFeaturesChange('refactoring')}
                                />
                            }
                            label="Refactoring"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.features.documentation}
                                    onChange={() => handleFeaturesChange('documentation')}
                                />
                            }
                            label="Documentation"
                        />
                    </Box>

                    <Divider sx={{ my: 3 }} />

                    <Typography variant="h6" gutterBottom>Preferences</Typography>
                    <Box sx={{ display: 'grid', gap: 2, mb: 3 }}>
                        <FormControl fullWidth>
                            <InputLabel>Language</InputLabel>
                            <Select
                                value={localSettings.preferences.language}
                                onChange={(e) => handlePreferencesChange('language', e.target.value)}
                                label="Language"
                            >
                                <MenuItem value="typescript">TypeScript</MenuItem>
                                <MenuItem value="javascript">JavaScript</MenuItem>
                                <MenuItem value="python">Python</MenuItem>
                                <MenuItem value="java">Java</MenuItem>
                                <MenuItem value="cpp">C++</MenuItem>
                            </Select>
                        </FormControl>

                        <FormControl fullWidth>
                            <InputLabel>Style</InputLabel>
                            <Select
                                value={localSettings.preferences.style}
                                onChange={(e) => handlePreferencesChange('style', e.target.value)}
                                label="Style"
                            >
                                <MenuItem value="concise">Concise</MenuItem>
                                <MenuItem value="detailed">Detailed</MenuItem>
                            </Select>
                        </FormControl>

                        <FormControl fullWidth>
                            <InputLabel>Suggestions Display</InputLabel>
                            <Select
                                value={localSettings.preferences.suggestions}
                                onChange={(e) => handlePreferencesChange('suggestions', e.target.value)}
                                label="Suggestions Display"
                            >
                                <MenuItem value="inline">Inline</MenuItem>
                                <MenuItem value="panel">Panel</MenuItem>
                            </Select>
                        </FormControl>

                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.preferences.autoComplete}
                                    onChange={(e) => handlePreferencesChange('autoComplete', e.target.checked)}
                                />
                            }
                            label="Auto Complete"
                        />
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={localSettings.preferences.autoExplain}
                                    onChange={(e) => handlePreferencesChange('autoExplain', e.target.checked)}
                                />
                            }
                            label="Auto Explain"
                        />
                    </Box>
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button onClick={() => onSave(localSettings)} variant="contained" color="primary">
                    Save Changes
                </Button>
            </DialogActions>
        </Dialog>
    );
}; 