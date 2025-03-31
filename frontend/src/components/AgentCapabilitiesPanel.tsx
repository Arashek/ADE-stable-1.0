import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Description as DescriptionIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { AgentService, GenerationType, ReviewType, TestType, DocumentationType } from '../services/agent.service';
import { useProject } from '../hooks/useProject';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`agent-tabpanel-${index}`}
      aria-labelledby={`agent-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export const AgentCapabilitiesPanel: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [capabilities, setCapabilities] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generationHistory, setGenerationHistory] = useState<any[]>([]);
  const [reviewHistory, setReviewHistory] = useState<any[]>([]);
  const [testHistory, setTestHistory] = useState<any[]>([]);
  const [docHistory, setDocHistory] = useState<any[]>([]);

  const { project } = useProject();
  const agentService = new AgentService();

  useEffect(() => {
    loadCapabilities();
  }, []);

  const loadCapabilities = async () => {
    try {
      setLoading(true);
      const caps = await agentService.getCapabilities();
      setCapabilities(caps);
      setError(null);
    } catch (err) {
      setError('Failed to load agent capabilities');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" action={<Button onClick={loadCapabilities}>Retry</Button>}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Paper sx={{ width: '100%', height: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="agent capabilities tabs">
          <Tab
            icon={<CodeIcon />}
            label="Code Generation"
            id="agent-tab-0"
            aria-controls="agent-tabpanel-0"
          />
          <Tab
            icon={<BugReportIcon />}
            label="Code Review"
            id="agent-tab-1"
            aria-controls="agent-tabpanel-1"
          />
          <Tab
            icon={<BugReportIcon />}
            label="Testing"
            id="agent-tab-2"
            aria-controls="agent-tabpanel-2"
          />
          <Tab
            icon={<DescriptionIcon />}
            label="Documentation"
            id="agent-tab-3"
            aria-controls="agent-tabpanel-3"
          />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <CodeGenerationPanel
          capabilities={capabilities?.code_generation}
          projectId={project?.id}
          onHistoryUpdate={setGenerationHistory}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <CodeReviewPanel
          capabilities={capabilities?.code_review}
          projectId={project?.id}
          onHistoryUpdate={setReviewHistory}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <TestingPanel
          capabilities={capabilities?.testing}
          projectId={project?.id}
          onHistoryUpdate={setTestHistory}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <DocumentationPanel
          capabilities={capabilities?.documentation}
          projectId={project?.id}
          onHistoryUpdate={setDocHistory}
        />
      </TabPanel>
    </Paper>
  );
};

// Code Generation Panel Component
const CodeGenerationPanel: React.FC<{
  capabilities: any;
  projectId: string;
  onHistoryUpdate: (history: any[]) => void;
}> = ({ capabilities, projectId, onHistoryUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    language: '',
    framework: '',
    requirements: '',
    constraints: '',
    generateTests: false,
    generateDocs: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const agentService = new AgentService();
      const result = await agentService.generateCode({
        project_id: projectId,
        language: formData.language,
        framework: formData.framework,
        requirements: formData.requirements.split('\n').filter(r => r.trim()),
        constraints: formData.constraints.split('\n').filter(c => c.trim()),
        metadata: {
          generate_tests: formData.generateTests,
          generate_docs: formData.generateDocs,
        },
      });

      // Update history
      const history = await agentService.getGenerationHistory(projectId);
      onHistoryUpdate(history);
    } catch (err) {
      setError('Failed to generate code');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Generate Code
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={formData.language}
                onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                label="Language"
              >
                {capabilities?.supported_languages.map((lang: string) => (
                  <MenuItem key={lang} value={lang}>
                    {lang}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Framework"
              value={formData.framework}
              onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Requirements"
              value={formData.requirements}
              onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Constraints"
              value={formData.constraints}
              onChange={(e) => setFormData({ ...formData, constraints: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Generate Code
            </Button>
          </Grid>
        </Grid>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

// Code Review Panel Component
const CodeReviewPanel: React.FC<{
  capabilities: any;
  projectId: string;
  onHistoryUpdate: (history: any[]) => void;
}> = ({ capabilities, projectId, onHistoryUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    filePath: '',
    reviewTypes: [] as string[],
    focusAreas: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const agentService = new AgentService();
      const result = await agentService.reviewCode({
        project_id: projectId,
        file_path: formData.filePath,
        review_types: formData.reviewTypes,
        focus_areas: formData.focusAreas.split('\n').filter(a => a.trim()),
      });

      // Update history
      const history = await agentService.getReviews(projectId);
      onHistoryUpdate(history);
    } catch (err) {
      setError('Failed to perform code review');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Code Review
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="File Path"
              value={formData.filePath}
              onChange={(e) => setFormData({ ...formData, filePath: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Review Types</InputLabel>
              <Select
                multiple
                value={formData.reviewTypes}
                onChange={(e) => setFormData({ ...formData, reviewTypes: e.target.value as string[] })}
                label="Review Types"
              >
                {capabilities?.types.map((type: string) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Focus Areas"
              value={formData.focusAreas}
              onChange={(e) => setFormData({ ...formData, focusAreas: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Review Code
            </Button>
          </Grid>
        </Grid>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

// Testing Panel Component
const TestingPanel: React.FC<{
  capabilities: any;
  projectId: string;
  onHistoryUpdate: (history: any[]) => void;
}> = ({ capabilities, projectId, onHistoryUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    filePath: '',
    testTypes: [] as string[],
    framework: '',
    coverageTarget: 80,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const agentService = new AgentService();
      const result = await agentService.generateTests({
        project_id: projectId,
        file_path: formData.filePath,
        test_types: formData.testTypes,
        framework: formData.framework,
        coverage_target: formData.coverageTarget,
      });

      // Update history
      const history = await agentService.getTestSuites(projectId);
      onHistoryUpdate(history);
    } catch (err) {
      setError('Failed to generate tests');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Generate Tests
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="File Path"
              value={formData.filePath}
              onChange={(e) => setFormData({ ...formData, filePath: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Test Types</InputLabel>
              <Select
                multiple
                value={formData.testTypes}
                onChange={(e) => setFormData({ ...formData, testTypes: e.target.value as string[] })}
                label="Test Types"
              >
                {capabilities?.types.map((type: string) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Framework"
              value={formData.framework}
              onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Coverage Target (%)"
              value={formData.coverageTarget}
              onChange={(e) => setFormData({ ...formData, coverageTarget: Number(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Generate Tests
            </Button>
          </Grid>
        </Grid>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

// Documentation Panel Component
const DocumentationPanel: React.FC<{
  capabilities: any;
  projectId: string;
  onHistoryUpdate: (history: any[]) => void;
}> = ({ capabilities, projectId, onHistoryUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    docTypes: [] as string[],
    format: 'markdown',
    style: 'default',
    includeExamples: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const agentService = new AgentService();
      const result = await agentService.generateDocumentation({
        project_id: projectId,
        doc_types: formData.docTypes,
        format: formData.format,
        style: formData.style,
        include_examples: formData.includeExamples,
      });

      // Update history
      const history = await agentService.getDocumentation(projectId);
      onHistoryUpdate(history);
    } catch (err) {
      setError('Failed to generate documentation');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Generate Documentation
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Documentation Types</InputLabel>
              <Select
                multiple
                value={formData.docTypes}
                onChange={(e) => setFormData({ ...formData, docTypes: e.target.value as string[] })}
                label="Documentation Types"
              >
                {capabilities?.types.map((type: string) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Format</InputLabel>
              <Select
                value={formData.format}
                onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                label="Format"
              >
                {capabilities?.formats.map((format: string) => (
                  <MenuItem key={format} value={format}>
                    {format}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Style"
              value={formData.style}
              onChange={(e) => setFormData({ ...formData, style: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Generate Documentation
            </Button>
          </Grid>
        </Grid>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
}; 