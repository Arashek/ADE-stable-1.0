import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Tabs,
  Tab,
  Code,
  Divider,
} from '@mui/material';
import {
  Code as CodeIcon,
  Description as DescriptionIcon,
  PlayArrow as PlayIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ApiDocs = () => {
  const [endpoints, setEndpoints] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEndpoints();
  }, []);

  const fetchEndpoints = async () => {
    try {
      const response = await fetch('/api/docs/endpoints');
      const data = await response.json();
      setEndpoints(data);
      if (data.length > 0) {
        setSelectedEndpoint(data[0]);
      }
    } catch (err) {
      setError('Failed to fetch API documentation');
    }
  };

  const handleEndpointSelect = (endpoint) => {
    setSelectedEndpoint(endpoint);
    setRequestBody('');
    setResponse(null);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSendRequest = async () => {
    if (!selectedEndpoint) return;

    setLoading(true);
    try {
      const response = await fetch(selectedEndpoint.url, {
        method: selectedEndpoint.method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestBody ? JSON.stringify(JSON.parse(requestBody)) : undefined,
      });

      const data = await response.json();
      setResponse(data);
    } catch (err) {
      setError('Failed to send request');
    } finally {
      setLoading(false);
    }
  };

  const renderEndpointList = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          API Endpoints
        </Typography>
        <List>
          {endpoints.map((endpoint) => (
            <ListItem
              key={endpoint.id}
              button
              selected={selectedEndpoint?.id === endpoint.id}
              onClick={() => handleEndpointSelect(endpoint)}
            >
              <ListItemIcon>
                <CodeIcon />
              </ListItemIcon>
              <ListItemText
                primary={endpoint.name}
                secondary={`${endpoint.method} ${endpoint.path}`}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const renderEndpointDetails = () => {
    if (!selectedEndpoint) return null;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {selectedEndpoint.name}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            {selectedEndpoint.method} {selectedEndpoint.path}
          </Typography>
          <Typography variant="body1" paragraph>
            {selectedEndpoint.description}
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Parameters
          </Typography>
          <List>
            {selectedEndpoint.parameters?.map((param) => (
              <ListItem key={param.name}>
                <ListItemText
                  primary={param.name}
                  secondary={`${param.type} - ${param.description}`}
                />
              </ListItem>
            ))}
          </List>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Request Body
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={requestBody}
            onChange={(e) => setRequestBody(e.target.value)}
            placeholder="Enter JSON request body"
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={handleSendRequest}
            disabled={loading}
          >
            Send Request
          </Button>

          {response && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Response
              </Typography>
              <SyntaxHighlighter
                language="json"
                style={vscDarkPlus}
                customStyle={{ borderRadius: 4 }}
              >
                {JSON.stringify(response, null, 2)}
              </SyntaxHighlighter>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderCodeExamples = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Code Examples
        </Typography>
        <List>
          {selectedEndpoint?.examples?.map((example, index) => (
            <React.Fragment key={index}>
              <ListItem>
                <ListItemText
                  primary={example.language}
                  secondary={
                    <SyntaxHighlighter
                      language={example.language.toLowerCase()}
                      style={vscDarkPlus}
                      customStyle={{ borderRadius: 4 }}
                    >
                      {example.code}
                    </SyntaxHighlighter>
                  }
                />
              </ListItem>
              {index < selectedEndpoint.examples.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Typography variant="h4" gutterBottom>
        API Documentation
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Endpoints" icon={<CodeIcon />} />
        <Tab label="Authentication" icon={<SecurityIcon />} />
        <Tab label="Settings" icon={<SettingsIcon />} />
      </Tabs>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          {renderEndpointList()}
        </Grid>
        <Grid item xs={12} md={8}>
          {activeTab === 0 && (
            <>
              {renderEndpointDetails()}
              {renderCodeExamples()}
            </>
          )}
          {activeTab === 1 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Authentication
                </Typography>
                <Typography paragraph>
                  All API requests require authentication using an API key. Include your API key in the request header:
                </Typography>
                <Code>
                  Authorization: Bearer YOUR_API_KEY
                </Code>
              </CardContent>
            </Card>
          )}
          {activeTab === 2 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  API Settings
                </Typography>
                <Typography paragraph>
                  Configure your API settings, rate limits, and webhooks here.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ApiDocs; 