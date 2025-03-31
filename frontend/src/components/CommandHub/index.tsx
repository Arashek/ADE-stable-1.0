import React from 'react';
import { Box, Paper, Tabs, Tab, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import DesignAgent from './DesignAgent';
import CodeAgent from './CodeAgent';
import AIAssistant from './AIAssistant';
import ToolsPanel from './ToolsPanel';

const StyledRoot = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}));

const StyledContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'hidden',
  position: 'relative',
}));

const StyledTabsContainer = styled(Box)(({ theme }) => ({
  borderBottom: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(2),
}));

interface CommandHubProps {
  activeAgent?: string;
  onSave?: (data: any) => void;
  onGenerateCode?: (data: any) => void;
  isGenerating?: boolean;
}

const CommandHub: React.FC<CommandHubProps> = ({
  activeAgent = 'design',
  onSave = () => {},
  onGenerateCode = () => {},
  isGenerating = false,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;
  
  const isDesignHubActive = currentPath.includes('design-hub');
  
  // If we're on a sub-route, show the Outlet component
  if (isDesignHubActive) {
    return <Outlet />;
  }

  const renderAgent = () => {
    switch (activeAgent) {
      case 'design':
        return (
          <DesignAgent
            projectId="ade-platform"
            onSave={onSave}
            onGenerateCode={onGenerateCode}
          />
        );
      case 'code':
        return (
          <CodeAgent
            projectId="ade-platform"
            onSave={onSave}
            onGenerateCode={onGenerateCode}
            isGenerating={isGenerating}
          />
        );
      case 'ai':
        return <AIAssistant />;
      case 'tools':
        return <ToolsPanel />;
      default:
        return <DesignAgent projectId="ade-platform" onSave={onSave} onGenerateCode={onGenerateCode} />;
    }
  };

  return (
    <StyledRoot>
      <StyledTabsContainer>
        <Tabs value={activeAgent} aria-label="command hub tabs">
          <Tab value="design" label="Design" />
          <Tab value="code" label="Code" />
          <Tab value="ai" label="AI" />
          <Tab value="tools" label="Tools" />
        </Tabs>
        <Button 
          variant="contained" 
          color="primary"
          sx={{ mt: 2, mb: 1 }}
          onClick={() => navigate('/command-hub/design-hub')}
        >
          Open Design Hub
        </Button>
      </StyledTabsContainer>
      <StyledContent>{renderAgent()}</StyledContent>
    </StyledRoot>
  );
};

export default CommandHub;