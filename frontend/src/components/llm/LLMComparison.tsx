import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Grid,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { EnhancedButton } from '../common/EnhancedButton';
import { FeedbackOverlay } from '../common/FeedbackOverlay';
import { llmService } from '../../services/llm.service';
import { monitoringService } from '../../services/monitoring.service';
import { accessibilityService } from '../../services/accessibility.service';

interface LLMComparisonProps {
  prompt: string;
  className?: string;
}

const Container = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  margin: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
}));

const ModelOutput = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(2),
  margin: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.default,
  minHeight: 200,
}));

const MetricChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
}));

const LoadingOverlay = styled(Box)({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(255, 255, 255, 0.7)',
  borderRadius: 'inherit',
});

export const LLMComparison: React.FC<LLMComparisonProps> = ({
  prompt,
  className,
}) => {
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (containerRef.current) {
      accessibilityService.addAriaLabel(
        containerRef.current,
        'LLM model comparison results'
      );
    }
  }, []);

  const handleGenerate = async (model: 'llama2' | 'mistral') => {
    setLoading((prev) => ({ ...prev, [model]: true }));
    setError(null);

    try {
      const result = await llmService.generateCompletion(prompt, {
        model,
        temperature: 0.7,
        maxTokens: 1000,
      });

      setResults((prev) => ({ ...prev, [model]: result }));

      monitoringService.trackUserEvent({
        type: 'llm_generation_complete',
        userId: 'anonymous',
        data: { model, promptLength: prompt.length },
      });
    } catch (err) {
      setError(`Error generating completion for ${model}`);
      monitoringService.trackError(err as Error, {
        context: 'llm_comparison',
        model,
      });
    } finally {
      setLoading((prev) => ({ ...prev, [model]: false }));
    }
  };

  const handleCompareAll = async () => {
    setLoading({ llama2: true, mistral: true });
    setError(null);

    try {
      const results = await llmService.compareModels(prompt, [
        { model: 'llama2' },
        { model: 'mistral' },
      ]);

      setResults(results);

      monitoringService.trackUserEvent({
        type: 'llm_comparison_complete',
        userId: 'anonymous',
        data: { promptLength: prompt.length },
      });
    } catch (err) {
      setError('Error comparing models');
      monitoringService.trackError(err as Error, {
        context: 'llm_comparison',
      });
    } finally {
      setLoading({ llama2: false, mistral: false });
    }
  };

  const renderModelOutput = (model: string) => {
    const result = results[model];
    const isLoading = loading[model];

    return (
      <ModelOutput
        key={model}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
      >
        <Box sx={{ position: 'relative', minHeight: 200 }}>
          {isLoading && (
            <LoadingOverlay>
              <CircularProgress />
            </LoadingOverlay>
          )}
          {result ? (
            <>
              <Typography variant="h6" gutterBottom>
                {model.toUpperCase()}
              </Typography>
              <Typography variant="body1" paragraph>
                {result.text}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <MetricChip
                  label={`Latency: ${result.latency.toFixed(2)}ms`}
                  color="primary"
                  variant="outlined"
                />
                <MetricChip
                  label={`Tokens: ${result.usage.totalTokens}`}
                  color="secondary"
                  variant="outlined"
                />
              </Box>
            </>
          ) : (
            <Typography variant="body1" color="text.secondary">
              No output generated yet
            </Typography>
          )}
        </Box>
      </ModelOutput>
    );
  };

  return (
    <Container ref={containerRef} className={className}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Model Comparison
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Compare outputs from different LLM models
        </Typography>
        <Box sx={{ mt: 2 }}>
          <EnhancedButton
            onClick={handleCompareAll}
            loading={loading.llama2 || loading.mistral}
            variant="primary"
            color="primary"
          >
            Compare All Models
          </EnhancedButton>
        </Box>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          {renderModelOutput('llama2')}
        </Grid>
        <Grid item xs={12} md={6}>
          {renderModelOutput('mistral')}
        </Grid>
      </Grid>

      <AnimatePresence>
        {error && (
          <FeedbackOverlay
            type="error"
            message={error}
            position="top"
            onClose={() => setError(null)}
          />
        )}
      </AnimatePresence>
    </Container>
  );
}; 