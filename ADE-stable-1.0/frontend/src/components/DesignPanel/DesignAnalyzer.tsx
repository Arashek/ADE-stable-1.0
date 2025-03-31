import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    Grid,
    CircularProgress,
    Rating,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
    CheckCircle as CheckIcon,
    Warning as WarningIcon,
    Error as ErrorIcon,
} from '@mui/icons-material';
import { DesignFeedback } from '../../types/design';
import { useDropzone } from 'react-dropzone';

interface DesignAnalyzerProps {
    onAnalyze: (design: any) => Promise<DesignFeedback>;
}

interface ScoreDisplayProps {
    score: number;
    label: string;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ score, label }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle1" sx={{ mr: 2, minWidth: 100 }}>
            {label}
        </Typography>
        <Rating
            value={score / 20}
            precision={0.5}
            readOnly
            sx={{ color: score >= 80 ? 'success.main' : score >= 60 ? 'warning.main' : 'error.main' }}
        />
        <Typography variant="body2" sx={{ ml: 1 }}>
            {score}/100
        </Typography>
    </Box>
);

export const DesignAnalyzer: React.FC<DesignAnalyzerProps> = ({ onAnalyze }) => {
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState<DesignFeedback | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        accept: {
            'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
            'application/json': ['.json']
        },
        onDrop: (acceptedFiles) => {
            setSelectedFile(acceptedFiles[0]);
        },
    });

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        setLoading(true);
        try {
            const design = await readFileContent(selectedFile);
            const result = await onAnalyze(design);
            setFeedback(result);
        } catch (error) {
            console.error('Error analyzing design:', error);
        } finally {
            setLoading(false);
        }
    };

    const readFileContent = (file: File): Promise<any> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const content = event.target?.result as string;
                    resolve(JSON.parse(content));
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = (error) => reject(error);
            reader.readAsText(file);
        });
    };

    const renderIssuesList = (items: string[], icon: React.ReactNode) => (
        <List dense>
            {items.map((item, index) => (
                <ListItem key={index}>
                    <ListItemIcon>{icon}</ListItemIcon>
                    <ListItemText primary={item} />
                </ListItem>
            ))}
        </List>
    );

    return (
        <Box sx={{ mt: 2 }}>
            <Paper
                {...getRootProps()}
                sx={{
                    p: 3,
                    mb: 3,
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'grey.300',
                    backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                    cursor: 'pointer',
                    textAlign: 'center',
                }}
            >
                <input {...getInputProps()} />
                <Typography variant="body1" gutterBottom>
                    {isDragActive
                        ? 'Drop the file here'
                        : 'Drag and drop a design file, or click to select'}
                </Typography>
                {selectedFile && (
                    <Typography variant="body2" color="primary">
                        Selected: {selectedFile.name}
                    </Typography>
                )}
            </Paper>

            <Button
                fullWidth
                variant="contained"
                color="primary"
                onClick={handleAnalyze}
                disabled={!selectedFile || loading}
                sx={{ mb: 3 }}
            >
                {loading ? 'Analyzing...' : 'Analyze Design'}
            </Button>

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {feedback && (
                <Box>
                    <Typography variant="h6" gutterBottom>
                        Analysis Results
                    </Typography>

                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={12} md={6}>
                            <ScoreDisplay score={feedback.analysis.usability.score} label="Usability" />
                            <ScoreDisplay score={feedback.analysis.accessibility.score} label="Accessibility" />
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <ScoreDisplay score={feedback.analysis.consistency.score} label="Consistency" />
                            <ScoreDisplay score={feedback.analysis.performance.score} label="Performance" />
                        </Grid>
                    </Grid>

                    <Divider sx={{ my: 3 }} />

                    <Typography variant="h6" gutterBottom>
                        Detailed Analysis
                    </Typography>

                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Usability Issues</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {renderIssuesList(feedback.analysis.usability.issues, <WarningIcon color="warning" />)}
                        </AccordionDetails>
                    </Accordion>

                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Accessibility Issues</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {renderIssuesList(feedback.analysis.accessibility.issues, <ErrorIcon color="error" />)}
                        </AccordionDetails>
                    </Accordion>

                    <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Recommendations</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            {renderIssuesList(
                                [
                                    ...feedback.analysis.usability.recommendations,
                                    ...feedback.analysis.accessibility.recommendations,
                                    ...feedback.analysis.consistency.recommendations,
                                    ...feedback.analysis.performance.recommendations,
                                ],
                                <CheckIcon color="success" />
                            )}
                        </AccordionDetails>
                    </Accordion>
                </Box>
            )}
        </Box>
    );
}; 