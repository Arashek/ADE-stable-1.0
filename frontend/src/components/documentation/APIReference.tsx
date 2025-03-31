import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  PlayArrow,
  Code,
  ExpandMore,
  ExpandLess,
  ContentCopy,
  Check,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Documentation } from '../../types/documentation';
import { MonitoringService } from '../../services/monitoring.service';

interface APIReferenceProps {
  doc: Documentation;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
}));

const EndpointHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(2),
}));

const MethodChip = styled(Chip)(({ theme }) => ({
  marginRight: theme.spacing(2),
  minWidth: 80,
}));

const getMethodColor = (method: string) => {
  switch (method.toLowerCase()) {
    case 'get':
      return '#4CAF50';
    case 'post':
      return '#2196F3';
    case 'put':
      return '#FF9800';
    case 'delete':
      return '#F44336';
    default:
      return '#757575';
  }
};

export const APIReference: React.FC<APIReferenceProps> = ({ doc }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  
  const monitoring = MonitoringService.getInstance();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleEndpointExpand = (endpointId: string) => {
    setExpandedEndpoint(expandedEndpoint === endpointId ? null : endpointId);
    
    // Track endpoint interaction
    monitoring.recordMetric({
      category: 'api_docs',
      name: 'endpoint_expanded',
      value: 1,
      tags: { endpoint: endpointId }
    });
  };

  const handleCopyCode = (code: string, language: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);

    // Track code copy
    monitoring.recordMetric({
      category: 'api_docs',
      name: 'code_copied',
      value: 1,
      tags: { language }
    });
  };

  const handleTryEndpoint = (endpoint: any) => {
    // Implement endpoint testing logic
    monitoring.recordMetric({
      category: 'api_docs',
      name: 'endpoint_tested',
      value: 1,
      tags: { 
        endpoint: endpoint.path,
        method: endpoint.method 
      }
    });
  };

  const renderEndpointExample = (endpoint: any) => {
    const codeExample = `curl -X ${endpoint.method.toUpperCase()} \\
  "${window.location.origin}${endpoint.path}" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(endpoint.example?.request || {}, null, 2)}'`;

    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle2">Example Request</Typography>
          <IconButton
            size="small"
            onClick={() => handleCopyCode(codeExample, 'bash')}
          >
            {copiedCode === codeExample ? <Check /> : <ContentCopy />}
          </IconButton>
        </Box>
        <SyntaxHighlighter
          language="bash"
          style={tomorrow}
          customStyle={{ borderRadius: 4 }}
        >
          {codeExample}
        </SyntaxHighlighter>
        {endpoint.example?.response && (
          <>
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
              Example Response
            </Typography>
            <SyntaxHighlighter
              language="json"
              style={tomorrow}
              customStyle={{ borderRadius: 4 }}
            >
              {JSON.stringify(endpoint.example.response, null, 2)}
            </SyntaxHighlighter>
          </>
        )}
      </Box>
    );
  };

  const renderEndpoint = (endpoint: any) => {
    const isExpanded = expandedEndpoint === endpoint.id;

    return (
      <StyledPaper key={endpoint.id}>
        <EndpointHeader>
          <MethodChip
            label={endpoint.method.toUpperCase()}
            sx={{ backgroundColor: getMethodColor(endpoint.method), color: 'white' }}
          />
          <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
            {endpoint.path}
          </Typography>
          <Button
            startIcon={<PlayArrow />}
            variant="outlined"
            size="small"
            onClick={() => handleTryEndpoint(endpoint)}
            sx={{ mr: 1 }}
          >
            Try It
          </Button>
          <IconButton
            size="small"
            onClick={() => handleEndpointExpand(endpoint.id)}
          >
            {isExpanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </EndpointHeader>
        <Typography variant="body2" color="textSecondary">
          {endpoint.description}
        </Typography>
        <Collapse in={isExpanded}>
          <Box sx={{ mt: 2 }}>
            {endpoint.parameters && (
              <>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Parameters
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Required</TableCell>
                        <TableCell>Description</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {endpoint.parameters.map((param: any) => (
                        <TableRow key={param.name}>
                          <TableCell>{param.name}</TableCell>
                          <TableCell>{param.type}</TableCell>
                          <TableCell>
                            {param.required ? (
                              <Chip size="small" label="Required" color="primary" />
                            ) : (
                              <Chip size="small" label="Optional" />
                            )}
                          </TableCell>
                          <TableCell>{param.description}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}
            {endpoint.example && (
              <Box sx={{ mt: 2 }}>
                {renderEndpointExample(endpoint)}
              </Box>
            )}
          </Box>
        </Collapse>
      </StyledPaper>
    );
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        API Reference
      </Typography>
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        sx={{ mb: 3 }}
      >
        <Tab label="REST API" />
        <Tab label="GraphQL" />
        <Tab label="WebSocket" />
      </Tabs>
      {activeTab === 0 && (
        <Box>
          {doc.endpoints?.map(endpoint => renderEndpoint(endpoint))}
        </Box>
      )}
      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            GraphQL Schema
          </Typography>
          <SyntaxHighlighter
            language="graphql"
            style={tomorrow}
            customStyle={{ borderRadius: 4 }}
          >
            {doc.graphqlSchema || '# No GraphQL schema available'}
          </SyntaxHighlighter>
        </Box>
      )}
      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            WebSocket Events
          </Typography>
          {doc.websocketEvents?.map(event => (
            <StyledPaper key={event.name}>
              <Typography variant="subtitle1">{event.name}</Typography>
              <Typography variant="body2" color="textSecondary">
                {event.description}
              </Typography>
            </StyledPaper>
          ))}
        </Box>
      )}
    </Box>
  );
};
