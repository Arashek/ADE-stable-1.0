import React, { useState } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Heading,
  Text,
  Textarea,
  Button,
  Select,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardBody,
  List,
  ListItem,
  Badge,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Divider,
} from '@chakra-ui/react';
import { ErrorAnalysisResponse, PatternMatchResponse, SolutionResponse } from './types';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [errorMessage, setErrorMessage] = useState('');
  const [stackTrace, setStackTrace] = useState('');
  const [domain, setDomain] = useState('');
  const [analysis, setAnalysis] = useState<ErrorAnalysisResponse | null>(null);
  const [patternMatches, setPatternMatches] = useState<PatternMatchResponse | null>(null);
  const [solution, setSolution] = useState<SolutionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error_message: errorMessage,
          stack_trace: stackTrace.split('\n'),
          domain: domain || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setAnalysis(data);
      toast({
        title: 'Analysis complete',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMatchPatterns = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/match-patterns`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error_message: errorMessage,
        }),
      });

      if (!response.ok) {
        throw new Error('Pattern matching failed');
      }

      const data = await response.json();
      setPatternMatches(data);
      toast({
        title: 'Pattern matching complete',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSolution = async (patternId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/generate-solution`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pattern_id: patternId,
        }),
      });

      if (!response.ok) {
        throw new Error('Solution generation failed');
      }

      const data = await response.json();
      setSolution(data);
      toast({
        title: 'Solution generated',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChakraProvider>
      <Box p={8}>
        <VStack spacing={8} align="stretch">
          <Heading>Error Analysis Platform</Heading>
          
          <Card>
            <CardBody>
              <VStack spacing={4}>
                <Textarea
                  placeholder="Enter error message"
                  value={errorMessage}
                  onChange={(e) => setErrorMessage(e.target.value)}
                  size="lg"
                  rows={4}
                />
                
                <Textarea
                  placeholder="Enter stack trace (optional)"
                  value={stackTrace}
                  onChange={(e) => setStackTrace(e.target.value)}
                  size="lg"
                  rows={6}
                />
                
                <Select
                  placeholder="Select domain (optional)"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                >
                  <option value="web_application">Web Application</option>
                  <option value="data_processing">Data Processing</option>
                  <option value="microservices">Microservices</option>
                  <option value="mobile_application">Mobile Application</option>
                </Select>
                
                <Button
                  colorScheme="blue"
                  onClick={handleAnalyze}
                  isLoading={loading}
                  loadingText="Analyzing..."
                >
                  Analyze Error
                </Button>
              </VStack>
            </CardBody>
          </Card>

          {analysis && (
            <Tabs>
              <TabList>
                <Tab>Analysis</Tab>
                <Tab>Pattern Matches</Tab>
                <Tab>Solution</Tab>
              </TabList>
              
              <TabPanels>
                <TabPanel>
                  <Card>
                    <CardBody>
                      <VStack spacing={4} align="stretch">
                        <Heading size="md">Error Analysis</Heading>
                        
                        <Box>
                          <Text fontWeight="bold">Analysis:</Text>
                          <Text>{analysis.error_analysis}</Text>
                        </Box>
                        
                        <Box>
                          <Text fontWeight="bold">Root Cause:</Text>
                          <Text>{analysis.root_cause}</Text>
                        </Box>
                        
                        <Box>
                          <Text fontWeight="bold">Confidence Score:</Text>
                          <Progress value={analysis.confidence_score * 100} colorScheme="green" />
                        </Box>
                        
                        <Box>
                          <Text fontWeight="bold">Solution Steps:</Text>
                          <List spacing={2}>
                            {analysis.solution_steps.map((step, index) => (
                              <ListItem key={index}>{step}</ListItem>
                            ))}
                          </List>
                        </Box>
                        
                        {analysis.impact_analysis && (
                          <Box>
                            <Text fontWeight="bold">Impact Analysis:</Text>
                            <SimpleGrid columns={2} spacing={4}>
                              {Object.entries(analysis.impact_analysis).map(([key, value]) => (
                                <Stat key={key}>
                                  <StatLabel>{key}</StatLabel>
                                  <StatNumber>{typeof value === 'object' ? JSON.stringify(value) : value}</StatNumber>
                                </Stat>
                              ))}
                            </SimpleGrid>
                          </Box>
                        )}
                        
                        {analysis.prevention_strategies && (
                          <Box>
                            <Text fontWeight="bold">Prevention Strategies:</Text>
                            <List spacing={2}>
                              {analysis.prevention_strategies.map((strategy, index) => (
                                <ListItem key={index}>{strategy}</ListItem>
                              ))}
                            </List>
                          </Box>
                        )}
                        
                        {analysis.monitoring_suggestions && (
                          <Box>
                            <Text fontWeight="bold">Monitoring Suggestions:</Text>
                            <List spacing={2}>
                              {analysis.monitoring_suggestions.map((suggestion, index) => (
                                <ListItem key={index}>{suggestion}</ListItem>
                              ))}
                            </List>
                          </Box>
                        )}
                      </VStack>
                    </CardBody>
                  </Card>
                </TabPanel>
                
                <TabPanel>
                  <Card>
                    <CardBody>
                      <VStack spacing={4} align="stretch">
                        <Heading size="md">Pattern Matches</Heading>
                        
                        {patternMatches?.matches.map((match, index) => (
                          <Card key={index} variant="outline">
                            <CardBody>
                              <VStack spacing={2} align="stretch">
                                <Text fontWeight="bold">{match.pattern_type}</Text>
                                <Text>{match.description}</Text>
                                
                                <Box>
                                  <Text fontWeight="bold">Confidence Score:</Text>
                                  <Progress value={patternMatches.confidence_scores[index] * 100} colorScheme="green" />
                                </Box>
                                
                                <Box>
                                  <Text fontWeight="bold">Context Similarity:</Text>
                                  <Progress value={patternMatches.context_similarity[index] * 100} colorScheme="blue" />
                                </Box>
                                
                                <Button
                                  colorScheme="green"
                                  onClick={() => handleGenerateSolution(match.pattern_id)}
                                  isLoading={loading}
                                  loadingText="Generating..."
                                >
                                  Generate Solution
                                </Button>
                              </VStack>
                            </CardBody>
                          </Card>
                        ))}
                      </VStack>
                    </CardBody>
                  </Card>
                </TabPanel>
                
                <TabPanel>
                  {solution && (
                    <Card>
                      <CardBody>
                        <VStack spacing={4} align="stretch">
                          <Heading size="md">Solution</Heading>
                          
                          <Box>
                            <Text fontWeight="bold">Description:</Text>
                            <Text>{solution.solution.description}</Text>
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold">Steps:</Text>
                            <List spacing={2}>
                              {solution.solution.steps.map((step, index) => (
                                <ListItem key={index}>{step}</ListItem>
                              ))}
                            </List>
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold">Confidence Score:</Text>
                            <Progress value={solution.confidence_score * 100} colorScheme="green" />
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold">Risk Assessment:</Text>
                            <List spacing={2}>
                              {Object.entries(solution.risk_assessment).map(([key, value]) => (
                                <ListItem key={key}>
                                  <Text fontWeight="bold">{key}:</Text>
                                  <Text>{typeof value === 'object' ? JSON.stringify(value) : value}</Text>
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold">Monitoring Plan:</Text>
                            <List spacing={2}>
                              {Object.entries(solution.monitoring_plan).map(([key, value]) => (
                                <ListItem key={key}>
                                  <Text fontWeight="bold">{key}:</Text>
                                  <Text>{typeof value === 'object' ? JSON.stringify(value) : value}</Text>
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                          
                          <Box>
                            <Text fontWeight="bold">Maintenance Requirements:</Text>
                            <List spacing={2}>
                              {solution.maintenance_requirements.map((req, index) => (
                                <ListItem key={index}>{req}</ListItem>
                              ))}
                            </List>
                          </Box>
                        </VStack>
                      </CardBody>
                    </Card>
                  )}
                </TabPanel>
              </TabPanels>
            </Tabs>
          )}
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

export default App; 