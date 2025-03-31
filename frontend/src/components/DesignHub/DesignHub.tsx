import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Tabs, 
  Tab, 
  Typography, 
  Paper, 
  Button, 
  IconButton,
  Divider,
  useMediaQuery,
  useTheme,
  CircularProgress,
  Snackbar,
  Alert,
  Drawer,
  FormControlLabel,
  Switch,
  Tooltip
} from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  Code as CodeIcon, 
  Palette as PaletteIcon, 
  Save as SaveIcon, 
  Visibility as PreviewIcon,
  ViewModule as ComponentsIcon,
  FormatPaint as StylesIcon,
  Chat as ChatIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  BugReport as ValidationIcon,
  Fullscreen as FullscreenIcon,
  DesktopWindows as DesktopIcon,
  PhoneAndroid as MobileIcon,
  Tablet as TabletIcon
} from '@mui/icons-material';
import { DesignSystem, DesignComponent, DesignPage, DesignSuggestion } from '../../types/design';
import { DesignAgent } from '../../services/DesignAgent';
import { DesignAgentService } from '../../services/DesignAgentService';
import { InteractiveDesignService } from '../../services/InteractiveDesignService';
import { DesignChat } from '../design/DesignChat';
import { DesignToolsPanel } from '../design/DesignToolsPanel';
import { DesignPreview } from '../design/DesignPreview';
import { DesignSuggestionsPanel } from '../design/DesignSuggestionsPanel';
import { DesignToolbar } from '../design/DesignToolbar';
import { ComponentLibrary } from '../design/ComponentLibrary';
import { StyleGuide } from '../design/StyleGuide';
import { DesignSystemConfig } from '../design/DesignSystemConfig';
import { DesignCanvas } from '../design/DesignCanvas';
import { useDesignAgent } from '../../hooks/useDesignAgent';

interface DesignHubProps {
  projectId?: string;
  onSaveDesign?: (design: DesignSystem) => void;
  onGenerateCode?: (design: DesignSystem) => void;
  initialDesign?: Partial<DesignSystem>;
}

type ViewMode = 'split' | 'design' | 'code' | 'preview';
type DevicePreview = 'desktop' | 'tablet' | 'mobile';
type DesignTab = 'canvas' | 'components' | 'styles' | 'chat' | 'validation' | 'settings' | 'history';

export const DesignHub: React.FC<DesignHubProps> = ({ 
  projectId, 
  onSaveDesign,
  onGenerateCode,
  initialDesign 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  
  // Design agent and services
  const { loading: agentLoading } = useDesignAgent();
  const [designAgent, setDesignAgent] = useState<any>(null);
  const [designAgentService] = useState(new DesignAgentService());
  const [interactiveService] = useState(new InteractiveDesignService());
  
  // Initialize design agent
  useEffect(() => {
    // Create a simplified agent interface that will work with our components
    setDesignAgent({
      generateDesignSuggestions: async (design: any) => {
        // This would call the actual design agent service
        try {
          return await designAgentService.generateSuggestions(design);
        } catch (error) {
          console.error('Error generating design suggestions:', error);
          return [];
        }
      },
      analyzeDesign: async (design: any) => {
        // This would call the actual design agent service
        try {
          return await designAgentService.analyzeDesign(design);
        } catch (error) {
          console.error('Error analyzing design:', error);
          return [];
        }
      }
    });
  }, [designAgentService]);
  
  // Design state
  const [currentDesign, setCurrentDesign] = useState<DesignSystem>(initialDesign as DesignSystem || {
    id: `design-${Date.now()}`,
    name: 'New Design',
    version: '1.0',
    components: [],
    pages: [
      {
        id: 'home',
        name: 'Home',
        components: []
      }
    ],
    currentPage: 'home',
    theme: {
      colors: {
        primary: '#3f51b5',
        secondary: '#f50057',
        background: '#ffffff',
        surface: '#f5f5f5',
        error: '#f44336',
        text: '#212121',
        textSecondary: '#757575'
      },
      typography: {
        fontFamily: 'Roboto, sans-serif',
        fontSize: 16,
        h1: { fontSize: '2.5rem', fontWeight: 500 },
        h2: { fontSize: '2rem', fontWeight: 500 },
        h3: { fontSize: '1.75rem', fontWeight: 500 },
        body: { fontSize: '1rem', fontWeight: 400 }
      },
      spacing: {
        unit: 8,
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32
      },
      borderRadius: {
        sm: 4,
        md: 8,
        lg: 16
      }
    }
  });
  
  const [currentPage, setCurrentPage] = useState<string>(currentDesign.currentPage || 'home');
  const [currentComponent, setCurrentComponent] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('split');
  const [devicePreview, setDevicePreview] = useState<DevicePreview>('desktop');
  const [currentTab, setCurrentTab] = useState<DesignTab>('canvas');
  const [isGeneratingCode, setIsGeneratingCode] = useState<boolean>(false);
  const [showCodePreview, setShowCodePreview] = useState<boolean>(false);
  const [codePreview, setCodePreview] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);
  const [isFullScreen, setIsFullScreen] = useState<boolean>(false);
  const [showTools, setShowTools] = useState<boolean>(!isMobile);
  const [autoSync, setAutoSync] = useState<boolean>(true);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  
  // History and undo/redo
  const [history, setHistory] = useState<DesignSystem[]>([currentDesign]);
  const [historyIndex, setHistoryIndex] = useState<number>(0);
  
  // Suggestions and agent feedback
  const [suggestions, setSuggestions] = useState<DesignSuggestion[]>([]);
  const [validationIssues, setValidationIssues] = useState<any[]>([]);
  const [refreshingDesign, setRefreshingDesign] = useState<boolean>(false);
  
  useEffect(() => {
    if (projectId) {
      setLoading(true);
      interactiveService.connectSession(projectId)
        .then(session => {
          if (session.design) {
            setCurrentDesign(session.design);
            setCurrentPage(session.design.currentPage || 'home');
          }
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to connect design session', err);
          setNotification({
            message: 'Failed to connect to design session',
            type: 'error'
          });
          setLoading(false);
        });
        
      // Cleanup on unmount
      return () => {
        interactiveService.disconnectSession(projectId);
      };
    }
  }, [projectId]);
  
  const handleSaveDesign = async () => {
    setLoading(true);
    try {
      if (projectId) {
        await interactiveService.saveDesign(projectId, currentDesign);
      }
      if (onSaveDesign) {
        onSaveDesign(currentDesign);
      }
      setLastSaved(new Date());
      setNotification({
        message: 'Design saved successfully',
        type: 'success'
      });
    } catch (error) {
      console.error('Failed to save design', error);
      setNotification({
        message: 'Failed to save design',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleGenerateCode = async () => {
    setIsGeneratingCode(true);
    try {
      const code = await designAgentService.generateCodeFromDesign(currentDesign);
      setCodePreview(code);
      setShowCodePreview(true);
      
      if (onGenerateCode) {
        onGenerateCode(currentDesign);
      }
    } catch (error) {
      console.error('Failed to generate code', error);
      setNotification({
        message: 'Failed to generate code',
        type: 'error'
      });
    } finally {
      setIsGeneratingCode(false);
    }
  };
  
  const handleUpdateDesign = (updatedDesign: Partial<DesignSystem>) => {
    const newDesign = { ...currentDesign, ...updatedDesign };
    setCurrentDesign(newDesign);
    
    // Add to history for undo/redo
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(newDesign);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    
    // Auto-save if enabled
    if (autoSync && projectId) {
      interactiveService.updateDesign(projectId, newDesign);
    }
  };
  
  const handleUpdateComponent = (componentId: string, updates: Partial<DesignComponent>) => {
    const updatedComponents = currentDesign.components?.map(component => 
      component.id === componentId ? { ...component, ...updates } : component
    );
    
    handleUpdateDesign({ components: updatedComponents });
  };
  
  const handlePageChange = (pageId: string) => {
    setCurrentPage(pageId);
    handleUpdateDesign({ currentPage: pageId });
  };
  
  const handleValidateDesign = async () => {
    setLoading(true);
    try {
      const issues = await designAgentService.validateDesign(currentDesign);
      setValidationIssues(issues);
      setCurrentTab('validation');
      
      // If no issues, show success message
      if (issues.length === 0) {
        setNotification({
          message: 'Design validation passed with no issues',
          type: 'success'
        });
      }
    } catch (error) {
      console.error('Failed to validate design', error);
      setNotification({
        message: 'Failed to validate design',
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleRefreshDesign = async () => {
    if (!designAgent) return;
    
    setRefreshingDesign(true);
    try {
      const suggestions = await designAgent.generateDesignSuggestions(currentDesign);
      setSuggestions(suggestions);
      
      setNotification({
        message: 'Design suggestions updated',
        type: 'info'
      });
    } catch (error) {
      console.error('Failed to refresh design suggestions', error);
      setNotification({
        message: 'Failed to get design suggestions',
        type: 'error'
      });
    } finally {
      setRefreshingDesign(false);
    }
  };
  
  const handleUndo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setCurrentDesign(history[newIndex]);
    }
  };
  
  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setCurrentDesign(history[newIndex]);
    }
  };
  
  const handleApplySuggestion = (suggestion: DesignSuggestion) => {
    if (suggestion.type === 'component') {
      const updatedComponents = [...(currentDesign.components || []), suggestion.component];
      handleUpdateDesign({ components: updatedComponents });
      
      // Add to current page if applicable
      if (currentPage) {
        const pageIndex = currentDesign.pages?.findIndex(page => page.id === currentPage);
        if (pageIndex !== undefined && pageIndex >= 0 && currentDesign.pages) {
          const updatedPages = [...currentDesign.pages];
          updatedPages[pageIndex] = {
            ...updatedPages[pageIndex],
            components: [...(updatedPages[pageIndex].components || []), suggestion.component.id]
          };
          handleUpdateDesign({ pages: updatedPages });
        }
      }
    } else if (suggestion.type === 'style') {
      handleUpdateDesign({ theme: { ...currentDesign.theme, ...suggestion.styles } });
    }
  };
  
  const handleCloseNotification = () => {
    setNotification(null);
  };
  
  const renderMainContent = () => {
    switch (currentTab) {
      case 'canvas':
        return (
          <DesignCanvas 
            currentDesign={currentDesign}
            currentPage={currentPage}
            onUpdateComponent={handleUpdateComponent}
            onAddComponent={(component) => {
              const updatedComponents = [...(currentDesign.components || []), component];
              
              // Add to current page components
              const pageIndex = currentDesign.pages?.findIndex(page => page.id === currentPage);
              if (pageIndex !== undefined && pageIndex >= 0 && currentDesign.pages) {
                const updatedPages = [...currentDesign.pages];
                updatedPages[pageIndex] = {
                  ...updatedPages[pageIndex],
                  components: [...(updatedPages[pageIndex].components || []), component.id]
                };
                
                handleUpdateDesign({ 
                  components: updatedComponents,
                  pages: updatedPages
                });
              }
            }}
            onSelectComponent={setCurrentComponent}
            onDeleteComponent={(componentId) => {
              const updatedComponents = currentDesign.components?.filter(c => c.id !== componentId);
              
              // Remove from current page components
              const pageIndex = currentDesign.pages?.findIndex(page => page.id === currentPage);
              if (pageIndex !== undefined && pageIndex >= 0 && currentDesign.pages) {
                const updatedPages = [...currentDesign.pages];
                updatedPages[pageIndex] = {
                  ...updatedPages[pageIndex],
                  components: updatedPages[pageIndex].components.filter(id => id !== componentId)
                };
                
                handleUpdateDesign({ 
                  components: updatedComponents,
                  pages: updatedPages
                });
              }
            }}
          />
        );
      case 'components':
        return (
          <ComponentLibrary 
            components={currentDesign.components || []}
            onAdd={(component) => {
              const updatedComponents = [...(currentDesign.components || []), component];
              handleUpdateDesign({ components: updatedComponents });
            }}
            onUpdate={handleUpdateComponent}
            onSelect={setCurrentComponent}
          />
        );
      case 'styles':
        return (
          <StyleGuide 
            theme={currentDesign.theme}
            onUpdate={(theme) => handleUpdateDesign({ theme })}
          />
        );
      case 'chat':
        return (
          <DesignChat 
            designAgent={designAgent}
            currentDesign={currentDesign}
            onUpdateDesign={handleUpdateDesign}
            onApplySuggestion={handleApplySuggestion}
          />
        );
      case 'validation':
        return (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Design Validation</Typography>
              <Button 
                startIcon={<ValidationIcon />} 
                variant="outlined" 
                onClick={handleValidateDesign}
                disabled={loading}
              >
                Validate Design
              </Button>
            </Box>
            
            {loading ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : validationIssues.length > 0 ? (
              <Paper variant="outlined" sx={{ p: 2 }}>
                {validationIssues.map((issue, index) => (
                  <Alert 
                    key={index} 
                    severity={issue.severity === 'HIGH' ? 'error' : issue.severity === 'MEDIUM' ? 'warning' : 'info'}
                    sx={{ mb: 1 }}
                  >
                    <Typography variant="subtitle2">{issue.description}</Typography>
                    <Typography variant="body2">{issue.fix_suggestion}</Typography>
                  </Alert>
                ))}
              </Paper>
            ) : (
              <Alert severity="success">No validation issues found!</Alert>
            )}
          </Box>
        );
      case 'settings':
        return (
          <DesignSystemConfig 
            currentDesign={currentDesign}
            onUpdateDesign={handleUpdateDesign}
          />
        );
      case 'history':
        return (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Design History</Typography>
              <Box>
                <Button 
                  onClick={handleUndo} 
                  disabled={historyIndex <= 0}
                  variant="outlined"
                  sx={{ mr: 1 }}
                >
                  Undo
                </Button>
                <Button 
                  onClick={handleRedo} 
                  disabled={historyIndex >= history.length - 1}
                  variant="outlined"
                >
                  Redo
                </Button>
              </Box>
            </Box>
            
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle1">
                {lastSaved ? `Last Saved: ${lastSaved.toLocaleTimeString()}` : 'Not saved yet'}
              </Typography>
              
              <Typography variant="subtitle2" mt={2} mb={1}>
                Changes History:
              </Typography>
              
              {history.map((design, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    p: 1, 
                    border: index === historyIndex ? `1px solid ${theme.palette.primary.main}` : 'none',
                    backgroundColor: index === historyIndex ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                    borderRadius: 1,
                    mb: 1,
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    setHistoryIndex(index);
                    setCurrentDesign(design);
                  }}
                >
                  <Typography variant="body2">
                    Version {index + 1}: {design.name} 
                    {index === 0 ? ' (Initial)' : ''}
                  </Typography>
                </Box>
              ))}
            </Paper>
          </Box>
        );
      default:
        return <Typography>Select a tab to continue</Typography>;
    }
  };
  
  const renderPreview = () => {
    if (viewMode === 'code' || (viewMode === 'split' && showCodePreview)) {
      return (
        <Paper 
          variant="outlined"
          sx={{ 
            p: 2, 
            height: '100%', 
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            backgroundColor: '#f5f5f5'
          }}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Generated Code</Typography>
            <Button 
              startIcon={<SaveIcon />}
              variant="contained"
              onClick={() => {
                // Save generated code
                if (onGenerateCode && codePreview) {
                  onGenerateCode(currentDesign);
                }
              }}
            >
              Save Code
            </Button>
          </Box>
          
          {isGeneratingCode ? (
            <Box display="flex" justifyContent="center" alignItems="center" height="80%">
              <CircularProgress />
            </Box>
          ) : (
            <pre>{codePreview || 'Click "Generate Code" to see the code preview'}</pre>
          )}
        </Paper>
      );
    }
    
    if (viewMode === 'preview' || (viewMode === 'split' && !showCodePreview)) {
      return (
        <DesignPreview 
          currentDesign={currentDesign}
          device={devicePreview}
          onClose={() => setViewMode('design')}
        />
      );
    }
    
    return null;
  };
  
  if (loading && !currentDesign.id) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box sx={{ 
      flexGrow: 1, 
      height: '100%',
      overflow: 'hidden',
      backgroundColor: theme.palette.background.default
    }}>
      {/* Main toolbar */}
      <Paper 
        elevation={1} 
        sx={{ 
          p: 1, 
          position: 'sticky', 
          top: 0, 
          zIndex: 10,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Box display="flex" alignItems="center">
          <Typography variant="h6" sx={{ mr: 2 }}>
            {currentDesign.name || 'Design Hub'}
          </Typography>
          
          <IconButton 
            onClick={() => setShowTools(!showTools)} 
            sx={{ mr: 1 }}
          >
            <PaletteIcon />
          </IconButton>
          
          <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Tooltip title="Desktop view">
              <IconButton 
                onClick={() => setDevicePreview('desktop')} 
                color={devicePreview === 'desktop' ? 'primary' : 'default'}
              >
                <DesktopIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Tablet view">
              <IconButton 
                onClick={() => setDevicePreview('tablet')} 
                color={devicePreview === 'tablet' ? 'primary' : 'default'}
              >
                <TabletIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Mobile view">
              <IconButton 
                onClick={() => setDevicePreview('mobile')} 
                color={devicePreview === 'mobile' ? 'primary' : 'default'}
              >
                <MobileIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Box>
          <Button 
            startIcon={<PreviewIcon />}
            variant="outlined"
            onClick={() => setViewMode(viewMode === 'preview' ? 'split' : 'preview')}
            sx={{ mr: 1 }}
          >
            Preview
          </Button>
          
          <Button 
            startIcon={<CodeIcon />}
            variant="outlined"
            onClick={handleGenerateCode}
            disabled={isGeneratingCode}
            sx={{ mr: 1 }}
          >
            Generate Code
          </Button>
          
          <Button 
            startIcon={<SaveIcon />}
            variant="contained"
            onClick={handleSaveDesign}
            disabled={loading}
          >
            Save
          </Button>
        </Box>
      </Paper>
      
      <Grid container spacing={0} sx={{ height: 'calc(100% - 64px)' }}>
        {/* Left panel - Tools */}
        <Drawer
          variant={isMobile ? "temporary" : "persistent"}
          open={showTools}
          onClose={() => setShowTools(false)}
          sx={{
            width: 240,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 240,
              boxSizing: 'border-box',
              position: isMobile ? 'fixed' : 'relative',
              height: '100%'
            },
          }}
        >
          <Tabs
            orientation="vertical"
            value={currentTab}
            onChange={(_, newValue) => setCurrentTab(newValue as DesignTab)}
            sx={{ borderRight: 1, borderColor: 'divider' }}
          >
            <Tab 
              icon={<PaletteIcon />} 
              label="Canvas" 
              value="canvas" 
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<ComponentsIcon />} 
              label="Components" 
              value="components" 
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<StylesIcon />} 
              label="Styles" 
              value="styles" 
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<ChatIcon />} 
              label="Chat" 
              value="chat" 
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<ValidationIcon />} 
              label="Validation" 
              value="validation" 
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<SettingsIcon />} 
              label="Settings" 
              value="settings" 
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<HistoryIcon />} 
              label="History" 
              value="history" 
              sx={{ minHeight: 64 }}
            />
          </Tabs>
        </Drawer>
        
        {/* Main content area */}
        <Grid 
          item 
          xs={12} 
          md={viewMode === 'split' ? 6 : 12} 
          lg={viewMode === 'split' ? 8 : 12}
          sx={{ 
            height: '100%', 
            overflow: 'auto', 
            p: 2,
            display: viewMode === 'preview' || viewMode === 'code' ? 'none' : 'block'
          }}
        >
          {renderMainContent()}
        </Grid>
        
        {/* Right panel - Preview or Code */}
        {(viewMode === 'split' || viewMode === 'preview' || viewMode === 'code') && (
          <Grid 
            item 
            xs={12} 
            md={viewMode === 'split' ? 6 : 12} 
            lg={viewMode === 'split' ? 4 : 12}
            sx={{ 
              height: '100%', 
              overflow: 'auto', 
              p: 2,
              borderLeft: viewMode === 'split' ? `1px solid ${theme.palette.divider}` : 'none'
            }}
          >
            {renderPreview()}
          </Grid>
        )}
      </Grid>
      
      {/* Suggestions panel */}
      {suggestions.length > 0 && (
        <Drawer
          anchor="right"
          open={suggestions.length > 0}
          onClose={() => setSuggestions([])}
          variant="persistent"
          sx={{
            width: 320,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 320,
              boxSizing: 'border-box',
            },
          }}
        >
          <DesignSuggestionsPanel 
            suggestions={suggestions}
            onApplySuggestion={handleApplySuggestion}
            onDismiss={() => setSuggestions([])}
          />
        </Drawer>
      )}
      
      {/* Notification */}
      <Snackbar 
        open={notification !== null} 
        autoHideDuration={6000} 
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        {notification && (
          <Alert onClose={handleCloseNotification} severity={notification.type}>
            {notification.message}
          </Alert>
        )}
      </Snackbar>
    </Box>
  );
};

// Helper for alpha color
function alpha(color: string, value: number): string {
  return color + Math.round(value * 255).toString(16).padStart(2, '0');
}

export default DesignHub;
