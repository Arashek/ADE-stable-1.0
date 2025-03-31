import React from 'react';
import {
  Box,
  Paper,
  makeStyles,
  Theme,
  createStyles,
} from '@material-ui/core';
import DesignAgent from './DesignAgent';
import CodeAgent from './CodeAgent';
import AIAssistant from './AIAssistant';
import ToolsPanel from './ToolsPanel';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    },
    content: {
      flex: 1,
      overflow: 'hidden',
      position: 'relative',
    },
  })
);

interface CommandHubProps {
  activeAgent: string;
  onSave: (data: any) => void;
  onGenerateCode: (data: any) => void;
  isGenerating: boolean;
}

const CommandHub: React.FC<CommandHubProps> = ({
  activeAgent,
  onSave,
  onGenerateCode,
  isGenerating,
}) => {
  const classes = useStyles();

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
        return (
          <AIAssistant
            projectId="ade-platform"
            isGenerating={isGenerating}
          />
        );
      case 'tools':
        return (
          <ToolsPanel
            projectId="ade-platform"
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className={classes.root}>
      <div className={classes.content}>
        {renderAgent()}
      </div>
    </div>
  );
};

export default CommandHub; 